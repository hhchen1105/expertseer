#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 11-08-2012
# Last Modified: Thu 08 Nov 2012 04:02:46 PM EST

import gflags
import random
import operator
import os
import sys

from collections import defaultdict
from mysql_util import init_db, close_db

FLAGS = gflags.FLAGS
gflags.DEFINE_integer('eval_paper_num', 0,
                      'Number of randomly selected papers for evaluation')

def usage(cmd):
  print 'Usage:', cmd, \
        '--eval_paper_num=VAL'
  return

def check_args(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError:
    print FLAGS

  if FLAGS.eval_paper_num == 0:
    usage(argv[0])
    raise Exception('eval_paper_num must be a positive integer')

def get_rand_papers(eval_paper_num):
  '''
  Return: list of tuples where each tuple contains
  (paper_cluster_id, paper_title, and paper_abstract)
  '''
  paper_infos = [ ]
  db, cursor = init_db()
  cursor.execute("""SELECT cluster, title, abstract FROM papers WHERE """ + \
                 """title IS NOT NULL AND title <> '' AND """ + \
                 """abstract IS NOT NULL AND abstract <> ''""")
  rows = cursor.fetchall()
  sampled_idx = random.sample(xrange(len(rows)), min(len(rows), eval_paper_num))
  for idx in sampled_idx:
    paper_infos.append((rows[idx]))

  close_db(db, cursor)
  return paper_infos

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

def get_longest_valid_term_list(term, trie):
  cur_valid_term_list = [ ]
  cur_valid_term_id = -1
  cur_valid_term_freq = -1
  cur_term_list = [ ]
  cur_trie = trie
  for word in term.split():
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

def inc_paper_keyphrase_ctr(paper_keyphrase_ctr, paper_clusterid, content, trie):
  content = content.lower()
  while len(content) > 0:
    valid_term_list, valid_term_id, valid_term_freq = \
        get_longest_valid_term_list(content, trie)
    if len(valid_term_list) == 0:
      content = ' '.join(content.split()[1:])
    else:
      paper_keyphrase_ctr[paper_clusterid][' '.join(valid_term_list)] += 1
      content = ' '.join(content.split()[len(valid_term_list):])

def get_paper_keyphrase_ctr(papers, trie):
  paper_keyphrase_ctr = defaultdict(lambda: defaultdict(int))
  sys.stdout.write('Generating paper_keyphrase_ctr\n')
  for i, paper in enumerate(papers):
    sys.stdout.write('\r%d / %d' % (i+1, len(papers)))
    paper_clusterid = paper[0]
    title = paper[1]
    abstract = paper[2]
    contents = title + ' >>> ' + abstract
    inc_paper_keyphrase_ctr(paper_keyphrase_ctr, paper_clusterid, contents, trie)
  sys.stdout.write('\n')
  return paper_keyphrase_ctr

def get_hist_num_keyphrase_of_paper(paper_keyphrase_ctr):
  hist = defaultdict(int)
  for paper_cid in paper_keyphrase_ctr:
    hist[len(paper_keyphrase_ctr[paper_cid])] += 1
  return hist

def get_keyphrase_doc_freq(paper_keyphrase_ctr):
  keyphrase_doc_freq_ctr = defaultdict(int)
  for paper_cid in paper_keyphrase_ctr:
    for keyphrase in paper_keyphrase_ctr[paper_cid]:
      keyphrase_doc_freq_ctr[keyphrase] += 1
  return keyphrase_doc_freq_ctr

def get_hist_keyphrase_doc_freq(keyphrase_doc_freq_ctr):
  hist = defaultdict(int)
  for keyphrase in keyphrase_doc_freq_ctr:
    hist[keyphrase_doc_freq_ctr[keyphrase]] += 1
  return hist

def remove_files_in_path(path):
  for f in os.listdir(path):
    os.remove(os.path.join(path, f))

def output_eval_results(keyphrase_doc_freq_ctr, hist_num_keyphrase_of_paper, hist_keyphrase_doc_freq):
  output_dir = 'outputs/keyphrase_eval/'
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  remove_files_in_path(output_dir)

  # output stats of how many candidate-keywords a document has
  f = open(os.path.join(output_dir, 'hist_num_keyphrase_of_paper_sample' + str(FLAGS.eval_paper_num)), 'w')
  f.write('doc_num_ratio\tkeyphrase_num\n')
  print 'Stats of number of keyphrases of sampled documents'
  for keyphrase_num in hist_num_keyphrase_of_paper:
    print '%d out of %d documents has %d keyphrases in title and abstract' \
        % (hist_num_keyphrase_of_paper[keyphrase_num], FLAGS.eval_paper_num, keyphrase_num)
    f.write('%f\t%d\n' % (float(hist_num_keyphrase_of_paper[keyphrase_num]) / FLAGS.eval_paper_num, keyphrase_num))
  print ''
  f.close()

  # output the document frequency ratio of the keyphrases
  f = open(os.path.join(output_dir, 'hist_keyphrase_doc_freq_sample' + str(FLAGS.eval_paper_num)), 'w')
  f.write('keyphrase_num\tdoc_freq_ratio\n')
  print 'Stats of document frequency of the keyphrases appearred in sampled documents'
  for doc_num in hist_keyphrase_doc_freq:
    print '%d keyphrases appear in %d out of %d sampled documents' \
        % (hist_keyphrase_doc_freq[doc_num], doc_num, FLAGS.eval_paper_num)
    f.write('%d\t%f\n' % (hist_keyphrase_doc_freq[doc_num], float(doc_num) / FLAGS.eval_paper_num))
  print ''
  f.close()

  # output the keyphrase details
  f = open(os.path.join(output_dir, 'keyphrase_df_detail_sample_' + str(FLAGS.eval_paper_num)), 'w')
  f.write('keyphrase\tdoc_freq\n')
  for keyphrase, doc_freq in sorted(keyphrase_doc_freq_ctr.iteritems(), key=operator.itemgetter(1), reverse=True):
    f.write('%s\t%d\n' % (keyphrase, doc_freq))
  f.close()

def main(argv):
  check_args(argv)

  papers = get_rand_papers(FLAGS.eval_paper_num)
  trie = gen_trie()
  paper_keyphrase_ctr = get_paper_keyphrase_ctr(papers, trie)
  keyphrase_doc_freq_ctr = get_keyphrase_doc_freq(paper_keyphrase_ctr)

  hist_num_keyphrase_of_paper = get_hist_num_keyphrase_of_paper(paper_keyphrase_ctr)
  hist_keyphrase_doc_freq = get_hist_keyphrase_doc_freq(keyphrase_doc_freq_ctr)
  output_eval_results(keyphrase_doc_freq_ctr, hist_num_keyphrase_of_paper, hist_keyphrase_doc_freq)

if __name__ == "__main__":
  main(sys.argv)

from nose.tools import assert_equal

class TestAll():
  def test_get_rand_papers(self):
    eval_paper_num = 10
    papers = get_rand_papers(eval_paper_num)
    assert_equal(len(papers), eval_paper_num)
    for paper in papers:
      assert_equal(len(paper), 3)

  def test_get_paper_keyphrase_ctr(self):
    eval_paper_num = 10
    papers = get_rand_papers(eval_paper_num)
    trie = gen_trie()
    paper_keyphrase_ctr = get_paper_keyphrase_ctr(papers, trie)
    assert_equal(len(paper_keyphrase_ctr), eval_paper_num)
    for paper_cid in paper_keyphrase_ctr:
      for keyphrase in paper_keyphrase_ctr[paper_cid]:
        assert_equal(self._in_trie(trie, keyphrase.split()), True)

  def _in_trie(self, trie, keyphrase):
    if len(keyphrase) == 1 and keyphrase[0] in trie:
      return '#' in trie[keyphrase[0]]
    if keyphrase[0] not in trie:
      return False
    return self._in_trie(trie[keyphrase[0]], keyphrase[1:])


