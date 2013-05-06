#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 18-09-2012
# Last Modified: Thu 20 Dec 2012 11:43:47 PM EST

import codecs
import itertools
import math
import os
import sys

from HTMLParser import HTMLParser
from collections import defaultdict

from mysql_util import init_db, close_db, is_tbl_exists

def usage(cmd):
  print 'Usage:', cmd
  return

class MLStripper(HTMLParser):
  def __init__(self):
    self.reset()
    self.fed = []
  def handle_data(self, d):
    self.fed.append(d)
  def get_data(self):
    return ''.join(self.fed)

def strip_tags(html):
  s = MLStripper()
  s.feed(html)
  return s.get_data()

def get_query_terms():
  query_terms = [ ]
  directory = 'outputs/title/'
  term_files = [filename for filename in os.listdir(directory) \
      if os.path.isfile(os.path.join(directory,filename))]
  for filename in term_files:
    f = codecs.open(os.path.join(directory, filename), mode='r', encoding='utf-8')
    for line in f:
      query_terms.append(line.strip().lower())
    f.close()
  return query_terms

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
  
def inc_keyphrase_ctr(keyphrase_ctr, content, trie):
  content = content.lower()
  while len(content) > 0:
    valid_term_list, valid_term_id, valid_term_freq = \
        get_longest_valid_term_list(content, trie)
    if len(valid_term_list) == 0:
      content = ' '.join(content.split()[1:])
    else:
      keyphrase_ctr[' '.join(valid_term_list)] += 1
      content = ' '.join(content.split()[len(valid_term_list):])

def match_keyphrases(content, trie):
  all_keyphrases = set()
  content = content.lower()
  while len(content) > 0:
    valid_term_list, valid_term_id, valid_term_freq = \
        get_longest_valid_term_list(content, trie)
    if len(valid_term_list) == 0:
      content = ' '.join(content.split()[1:])
    else:
      all_keyphrases.add(' '.join(valid_term_list))
      content = ' '.join(content.split()[len(valid_term_list):])
  return list(all_keyphrases)

def inc_keyphrase_relation_ctr(keyphrase_relation_ctr, contents, trie):
  all_keyphrases = match_keyphrases(contents, trie)
  for pair in itertools.permutations(all_keyphrases, 2):
    keyphrase_relation_ctr[pair[0]][pair[1]] += 1

def get_ngram_info_by_name(db, cursor, name):
  cursor.execute("""SELECT id, freq FROM ngrams WHERE name=%s""", (name))
  row = cursor.fetchone()
  return row

def save_one_existing_keyphrase_to_table(db, cursor, ngram_id, ngram_freq, addend):
  freq = ngram_freq + addend
  try:
    cursor.execute("""UPDATE ngrams SET freq = %s WHERE id = %s""", \
        (freq, ngram_id))
    db.commit()
  except:
    sys.stderr.write('Error in updating table ngrams of id ' + str(ngram_id) + '\n')
    db.rollback()

def upd_keyphrase_ctr_to_table(db, cursor, keyphrase_ctr):
  for k in keyphrase_ctr:
    ngram_info = get_ngram_info_by_name(db, cursor, k)
    if ngram_info == None:
      raise Exception('Error in getting ngram_info, ngram_info should not be None')
    else:
      save_one_existing_keyphrase_to_table(db, cursor, ngram_info[0], ngram_info[1], keyphrase_ctr[k])

def get_ngram_id_by_name(db, cursor, name):
  cursor.execute("""SELECT id FROM ngrams WHERE name=%s""", (name))
  row = cursor.fetchone()
  return row[0]

def get_ngram_relation_info_by_ids(db, cursor, id1, id2):
  cursor.execute("""SELECT id, co_occur FROM ngram_relations WHERE src_id=%s and tar_id=%s""", (id1, id2))
  row = cursor.fetchone()
  return row

def save_existing_keyphrase_relation_ctr_to_table(db, cursor, ngram_relation_id, ngram_relation_co_occur, addend):
  try:
    cursor.execute("""UPDATE ngram_relations SET co_occur = %s WHERE id = %s""", \
        (ngram_relation_co_occur+addend, ngram_relation_id))
    db.commit()
  except:
    sys.stderr.write('Error in updating table ngram_relations of id ' + str(ngram_relation_id) + '\n')
    db.rollback()

def save_one_keyphrase_relation_to_table(db, cursor, id1, id2, init_co_occur):
  if id1 == id2:
    return
  try:
    cursor.execute("""INSERT INTO ngram_relations (src_id, tar_id, co_occur) VALUES (%s, %s, %s)""", \
        (id1, id2, init_co_occur))
    db.commit()
  except:
    sys.stderr.write('Error in inserting table ngram_relations of ids ' + str(id1) + ', ' + str(id2) + '\n')
    db.rollback()

def upd_keyphrase_relation_ctr_to_table(db, cursor, keyphrase_relation_ctr):
  for k1 in keyphrase_relation_ctr:
    for k2 in keyphrase_relation_ctr[k1]:
      id1 = get_ngram_id_by_name(db, cursor, k1)
      id2 = get_ngram_id_by_name(db, cursor, k2)
      keyphrase_relation_info = get_ngram_relation_info_by_ids(db, cursor, id1, id2)
      if keyphrase_relation_info == None:
        save_one_keyphrase_relation_to_table(db, cursor, id1, id2, keyphrase_relation_ctr[k1][k2])
      else:
        save_existing_keyphrase_relation_ctr_to_table(db, cursor, \
            keyphrase_relation_info[0], keyphrase_relation_info[1], keyphrase_relation_ctr[k1][k2])

def get_freq_by_ngram_id(db, cursor, id):
  cursor.execute("""SELECT freq FROM ngrams WHERE id=%s""", (id))
  row = cursor.fetchone()
  if row == None:
    raise Exception('Error in get_freq_by_ngram_id(db, cursor, ' + str(id) + ')\n')
  return row[0]

def pmi(x, y, xy):
  return math.log(float(xy)/(x*y))

def normalize(v, orig_min, orig_max, new_min, new_max):
  if orig_min > v or orig_max < v:
    raise Exception("Error in normalize(), orig_min=%s, v=%s, orig_max=%s" %(orig_min, v, orig_max))
  return new_min + (float(v) - orig_min) * (new_max - new_min) / (orig_max - orig_min)

def get_total_freq(db, cursor):
  cursor.execute("""SELECT sum(freq) FROM ngrams""")
  row = cursor.fetchone()
  return row[0]

def upd_co_occur_norm():
  db, cursor = init_db()
  total_freq = float(get_total_freq(db, cursor))
  cursor.execute("""SELECT id, src_id, tar_id, co_occur FROM ngram_relations""")
  rows = cursor.fetchall()
  for r in rows:
    id = r[0]
    src_freq_prob = get_freq_by_ngram_id(db, cursor, r[1]) / total_freq
    tar_freq_prob = get_freq_by_ngram_id(db, cursor, r[2]) / total_freq
    co_occur_prob = r[3] / total_freq
    co_occur_norm = normalize(pmi(src_freq_prob, tar_freq_prob, co_occur_prob) / (-math.log(co_occur_prob)), -1, 1, 1, 5)
    try:
      cursor.execute("""UPDATE ngram_relations SET co_occur_norm = %s WHERE id = %s""",
          (co_occur_norm, id))
      db.commit()
    except:
      sys.stderr.write('Error in updating table ngrams of id "' + str(id) + '"\n')
      db.rollback()
  close_db(db, cursor)

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

def gen_keyphrase_info(trie):
  db, cursor = init_db()
  if not is_tbl_exists(db, cursor, 'ngram_relations'):
    cursor.execute('CREATE TABLE ngram_relations '  + \
        '(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ' + \
        'src_id INT NOT NULL, ' + \
        'tar_id INT NOT NULL, ' + \
        'co_occur INT DEFAULT 0, ' + \
        'co_occur_norm FLOAT DEFAULT 0, ' + \
        'is_valid INT(1) DEFAULT 1, ' + \
        'UNIQUE src_tar_idx (src_id, tar_id))')

  batch_save_size = 100
  keyphrase_ctr = defaultdict(int)
  keyphrase_relation_ctr = defaultdict(lambda : defaultdict(int))
  cursor.execute("""SELECT title, abstract FROM papers""")
  rows = cursor.fetchall()
  num_rows = len(rows)
  sys.stdout.write('Generating keyphrase information\n')
  for i, r in enumerate(rows):
    sys.stdout.write("\r%d / %d" % (i+1, num_rows))
    contents = r[0].lower() + ' >>> ' if r[0] is not None else ''
    if r[1] is not None:
      contents += r[1].lower()
    inc_keyphrase_ctr(keyphrase_ctr, contents, trie)
    inc_keyphrase_relation_ctr(keyphrase_relation_ctr, contents, trie)
    if (i+1) % batch_save_size == 0:
      upd_keyphrase_ctr_to_table(db, cursor, keyphrase_ctr)
      upd_keyphrase_relation_ctr_to_table(db, cursor, keyphrase_relation_ctr)
      keyphrase_ctr = defaultdict(int)
      keyphrase_relation_ctr = defaultdict(lambda : defaultdict(int))
  upd_keyphrase_ctr_to_table(db, cursor, keyphrase_ctr)
  upd_keyphrase_relation_ctr_to_table(db, cursor, keyphrase_relation_ctr)
  upd_co_occur_norm()
  sys.stdout.write("\n")
  #cursor.execute('ALTER TABLE ngram_relations ADD UNIQUE INDEX (src_id, tar_id)')
  close_db(db, cursor)

def main(argv):
  trie = gen_trie()
  gen_keyphrase_info(trie)

if __name__ == "__main__":
  main(sys.argv)


# testing codes below
from nose.tools import assert_equal
class TestAll():
  def test_normalize(self):
    assert_equal(normalize(0, -1, 1, 1, 5), 3)
    assert_equal(normalize(1, -1, 1, 1, 5), 5)
    assert_equal(normalize(-1, -1, 1, 1, 5), 1)
    assert_equal(normalize(0.5, -1, 1, 1, 5), 4)
    assert_equal(normalize(0.9, -1, 1, 1, 5), 4.8)

