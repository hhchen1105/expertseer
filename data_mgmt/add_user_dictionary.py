#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 12-19-2012
# Last Modified: Mon 06 May 2013 01:30:17 PM EDT

import codecs
import sys

from mysql_util import init_db, close_db

def get_user_defined_terms():
  user_defined_terms = set()
  f = codecs.open('./settings/user_dictionary', mode='r', encoding='utf-8')
  for line in f:
    user_defined_terms.add(line.strip().lower())
  f.close()
  return user_defined_terms

def is_term_in_ngrams(db, cursor, term):
  cursor.execute("""SELECT id FROM ngrams WHERE name=%s""", (term))
  row = cursor.fetchone()
  return row is not None

def add_to_ngrams(user_defined_terms):
  db, cursor = init_db()
  for term in user_defined_terms:
    if not is_term_in_ngrams(db, cursor, term):
      try:
        cursor.execute("""INSERT INTO ngrams (name, n) VALUES (%s, %s)""", \
                       (term, len(term.split())))
        db.commit()
      except:
        sys.stderr.write('Error in inserting table ngrams "' + term + '"\n')
        db.rollback()
  close_db(db, cursor)

def main(argv):
  user_defined_terms = get_user_defined_terms()
  add_to_ngrams(user_defined_terms)

if __name__ == "__main__":
  main(sys.argv)

from nose.tools import assert_equal

class TestAll():
  def test_foo(self):
    assert_equal(1, 1)
