#!/usr/bin/env python

import gflags
import math
import sys

from collections import defaultdict
from mysql_util import init_db, close_db, is_tbl_exists

FLAGS = gflags.FLAGS
gflags.DEFINE_string('output', '', 'output file for the generated trie')

def usage(cmd):
  print 'Usage:', cmd
  return

def insert_trie(trie, ngram_id, name):
  if name:
    name = name.split()
    first, rest = name[0].lower(), ' '.join(name[1:])
    if first not in trie:
      trie[first] = { }
    insert_trie(trie[first], ngram_id, rest)
  else:
    if '#' in trie:
      trie['#'] += 1
    else:
      trie['#'] = 1
      trie['#id'] = ngram_id

def gen_trie():
  db, cursor = init_db()

  trie = { }
  cursor.execute("""SELECT id, name FROM ngrams WHERE is_valid = 1""")
  rows = cursor.fetchall()
  n_rows = len(rows)
  sys.stdout.write('Generating trie\n')
  for i, r in enumerate(rows):
    sys.stdout.write("\r%d / %d" % (i+1, n_rows))
    ngram_id = r[0]
    name = r[1]
    insert_trie(trie, ngram_id, name)
  sys.stdout.write('\n')

  close_db(db, cursor)
  return trie

def get_author_clusters():
  db, cursor = init_db()

  author_clusters = [ ]
  cursor.execute("""SELECT distinct(cluster) FROM authors""")
  rows = cursor.fetchall()
  for r in rows:
    author_clusters.append(r[0])

  close_db(db, cursor)
  return author_clusters

def get_longest_valid_term_list(term, trie):
  cur_valid_term_list = [ ]
  cur_valid_term_id = -1
  cur_valid_term_freq = -1
  cur_term_list = [ ]
  cur_trie = trie
  for word in term.split():
    if word == '#':
      continue
    if word in cur_trie.keys() and '#' in cur_trie[word]:
      cur_valid_term_list = cur_term_list + [word]
      cur_valid_term_id = cur_trie[word]['#id']
      cur_valid_term_freq = cur_trie[word]['#']
      cur_term_list.append(word)
      cur_trie = cur_trie[word]
    elif word in cur_trie.keys() and '#' not in cur_trie[word]:
      cur_term_list.append(word)
      cur_trie = cur_trie[word]
    else:
      break
  return cur_valid_term_list, cur_valid_term_id, cur_valid_term_freq

def gen_term_ctr(content, trie):
  term_ctr = defaultdict(int)
  content = content.lower()
  while len(content) > 0:
    valid_term_list, valid_term_id, valid_term_freq = \
        get_longest_valid_term_list(content, trie)
    if len(valid_term_list) == 0:
      content = ' '.join(content.split()[1:])
    else:
      term_ctr[valid_term_id] += 1
      content = ' '.join(content.split()[len(valid_term_list):])
  return term_ctr

def upd_author_keyphrase(author_keyphrase, author_cluster, term_ctr, ncites):
  if author_cluster not in author_keyphrase.keys():
    author_keyphrase[author_cluster] = { }
  for term_id in term_ctr:
    if term_id not in author_keyphrase[author_cluster]:
      author_keyphrase[author_cluster][term_id] = \
          [term_ctr[term_id], term_ctr[term_id] * math.log(math.exp(1) + ncites)]
    else:
      author_keyphrase[author_cluster][term_id][0] += term_ctr[term_id]
      author_keyphrase[author_cluster][term_id][1] += term_ctr[term_id] * math.log(math.exp(1) + ncites)

def gen_author_keyphrase(trie):
  # ex: Assuming sean's author cluster is 203, sean is good at nuclear (id = 2111) and oxygen (id=76),
  #     then: author_keyphrase[203] = {2111: 3, 76: 5}, where 3 and 5 are the appearance frequency
  #     of nuclear and oxygen in his publications
  batch_save_size = 100
  db, cursor = init_db()

  if not is_tbl_exists(db, cursor, 'personal_keywords'):
    cursor.execute('CREATE TABLE personal_keywords (' + \
                   'id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ' + \
                   'person_cluster int, ' + \
                   'ngram_id int, ' + \
                   'year int, ' + \
                   'count int, ' + \
                   'log_cite_prod_count float)')

  author_clusters = get_author_clusters()
  author_keyphrase = { }
  sys.stdout.write("Generating author_keyphrase\n")
  n_author_clusters = len(author_clusters)
  for i, author_cluster in enumerate(author_clusters):
    sys.stdout.write("\r%d / %d" % (i+1, n_author_clusters))
    cursor.execute("""SELECT authors.cluster, papers.title, """ + \
        """papers.abstract, papers.ncites FROM authors, papers WHERE """ + \
        """authors.paper_cluster = papers.cluster and authors.cluster = %s""", (author_cluster))
    rows = cursor.fetchall()
    for r in rows:
      author_cluster = r[0]
      contents = r[1].lower() + ' >>> ' if r[1] is not None else ''
      if r[2] is not None:
        contents += r[2].lower()
      ncites = r[3]
      term_ctr = gen_term_ctr(contents, trie)
      upd_author_keyphrase(author_keyphrase, author_cluster, term_ctr, ncites)
    if (i+1) % batch_save_size == 0:
      save_author_keyphrase_to_table(db, cursor, author_keyphrase)
      author_keyphrase = { }
  save_author_keyphrase_to_table(db, cursor, author_keyphrase)
  sys.stdout.write("\nCreating indexes...\n")
  cursor.execute('ALTER TABLE personal_keywords ADD INDEX (person_cluster), ' + \
                 'ADD INDEX (ngram_id), ADD INDEX (year)')
  close_db(db, cursor)

def save_author_keyphrase_to_table(db, cursor, author_keyphrase):
  for author_cluster in author_keyphrase:
    for ngram_id in author_keyphrase[author_cluster]:
      try:
        cursor.execute("""INSERT INTO personal_keywords """ + \
            """(person_cluster, ngram_id, count, log_cite_prod_count) """ + \
            """VALUES (%s, %s, %s, %s)""", \
            (author_cluster, ngram_id, author_keyphrase[author_cluster][ngram_id][0], \
            author_keyphrase[author_cluster][ngram_id][1]))
        db.commit()
      except:
        sys.stderr.write("\nError in writing (person_cluster, ngram_id, count) values (%d, %d, %d)\n" \
            % (author_cluster, ngram_id, author_keyphrase[author_cluster][ngram_id]))
        db.rollback()

def main(argv):
  # Parse flags
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError:
    print FLAGS

  trie = gen_trie()
  gen_author_keyphrase(trie)

if __name__ == "__main__":
  main(sys.argv)


