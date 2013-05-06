#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 11-08-2012
# Last Modified: Mon 06 May 2013 01:31:08 PM EDT

import codecs
import gflags
import os
import sys

from mysql_util import init_db, close_db, is_tbl_exists

FLAGS = gflags.FLAGS

def usage(cmd):
  print 'Usage:', cmd, \
        '--arg1="VAL"'
  return

def check_args(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError:
    print FLAGS

def invalidate_stopwords_from_keyphrases(stopwords):
  db, cursor = init_db()
  if not is_tbl_exists(db, cursor, 'ngrams'):
    raise Exception('Table "ngrams" does not exist!')
  for stopword in stopwords:
    try:
      cursor.execute("""UPDATE ngrams SET is_valid=0 WHERE name=%s""", \
          (stopword))
      db.commit()
    except:
      db.rollback()
      raise Exception('Error in updating table "ngrams"')
  close_db(db, cursor)

def get_stopwords():
  filename = './settings/stopwords'
  if not os.path.isfile(filename):
    raise Exception('The file to specify the stopwords does not exist.  ' + \
                    'Please create a file "./settings/stopwords".  ' + \
                    'Each line of the file put one stopword.')
  stopwords = [ ]
  f = codecs.open(filename, mode='r', encoding='utf-8')
  for line in f:
    stopwords.append(line.strip())
  f.close()
  return stopwords

def main(argv):
  check_args(argv)

  stopwords = get_stopwords()
  invalidate_stopwords_from_keyphrases(stopwords)

if __name__ == "__main__":
  main(sys.argv)

from nose.tools import assert_equal

class TestAll():
  def test_foo(self):
    assert_equal(1, 1)
