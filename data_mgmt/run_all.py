#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 12-19-2012
# Last Modified: Fri 12 Apr 2013 05:10:55 PM EDT

import gflags
import os
import sys

FLAGS = gflags.FLAGS
gflags.DEFINE_bool('is_parse_wiki', True, '')

def usage(cmd):
  print 'Usage:', cmd, \
        '--is_parse_wiki=False'
  return

def check_args(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError:
    print FLAGS

def run_cmd(cmd):
  print cmd
  os.system(cmd)

def run_all():
  if FLAGS.is_parse_wiki:
    run_cmd('./wiki_gen_sub_category_and_title_from_category.py')
    run_cmd('./wiki_gen_keyphrases.py')
  run_cmd('./add_user_dictionary.py')
  run_cmd('./remove_stopwords.py')
  run_cmd('./match_corpus_keyphrases.py')
  run_cmd('./gen_personal_keywords_wiki.py')
  run_cmd('./create_solr_docs.py')

def main(argv):
  check_args(argv)
  run_all()

if __name__ == "__main__":
  main(sys.argv)

from nose.tools import assert_equal

class TestAll():
  def test_foo(self):
    assert_equal(1, 1)
