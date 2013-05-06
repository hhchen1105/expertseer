#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 05-01-2013
# Last Modified: Mon 06 May 2013 01:46:54 PM EDT

import gflags
import os
import sys

import mysql_util

FLAGS = gflags.FLAGS

def usage(cmd):
  print 'Usage:', cmd
  return

def check_args(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError:
    print FLAGS

def database_reset_confirmation():
  db_info = mysql_util.get_db_info()
  user_input = raw_input('You are testing using database "' + db_info['db'] + \
                         '".\nThis testing will effect the tables in this database.\n' + \
                         'Do you want to continue (n/y)? ')
  if user_input != 'y' and user_input != 'Y':
    print 'Testing is cancelled'
    sys.exit()

def drop_tables():
  print 'Dropping tables'
  db, cursor = mysql_util.init_db()
  tables_to_be_removed = mysql_util.get_all_tbl(db, cursor)
  for tbl in tables_to_be_removed:
    mysql_util.drop_tbl(db, cursor, tbl)
  mysql_util.close_db(db, cursor)

def import_ngrams_tbl():
  print 'Importing ngrams table'
  db_info = mysql_util.get_db_info()
  ngram_import_cmd = 'mysql -u' + db_info['user'] + ' -p' + db_info['passwd'] + \
      ' ' + db_info['db'] + ' < ./settings/test_sql/ngrams.sql'
  os.system(ngram_import_cmd)

def import_papers_and_authors_tbl():
  print 'Importing papers and authors table'
  db_info = mysql_util.get_db_info()
  ngram_import_cmd = 'mysql -u' + db_info['user'] + ' -p' + db_info['passwd'] + \
      ' ' + db_info['db'] + ' < ./settings/test_sql/testseers.sql'
  os.system(ngram_import_cmd)

def gen_required_tables():
  import_ngrams_tbl()
  import_papers_and_authors_tbl()
  os.system('./run_all.py --is_parse_wiki=False')

def main(argv):
  check_args(argv)

  database_reset_confirmation()
  drop_tables()
  gen_required_tables()

if __name__ == "__main__":
  main(sys.argv)

