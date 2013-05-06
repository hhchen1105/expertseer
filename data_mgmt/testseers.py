#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 12-03-2012
# Last Modified: Wed 19 Dec 2012 02:05:00 PM EST

import os
import sys
import unittest

from mysql_util import init_db, close_db, is_tbl_exists, get_db_info, drop_tbl

def database_reset_confirmation():
  db_info = get_db_info()
  user_input = raw_input('You are testing using database "' + db_info['db'] + \
                         '".\nThis testing will effect the tables in this database.\n' + \
                         'Do you want to continue (n/y)? ')
  if user_input != 'y' and user_input != 'Y':
    print 'Testing is cancelled'
    sys.exit()

def reset_tables_for_testing(db, cursor):
  tables_to_be_removed = [ 'ngram_relations', 'personal_keywords', 'root_categories']
  for tbl in tables_to_be_removed:
    drop_tbl(db, cursor, tbl)
  reset_ngram_freq(db, cursor)

def reset_tables():
  db, cursor = init_db()
  check_required_tables(db, cursor)
  reset_tables_for_testing(db, cursor)
  close_db(db, cursor)

def reset_ngram_freq( db, cursor):
  cursor.execute("""SELECT id FROM ngrams WHERE freq > 0""")
  rows = cursor.fetchall()
  ids = [r[0] for r in rows]
  for id in ids:
    try:
      cursor.execute("""UPDATE ngrams SET freq = 0 WHERE id = %s""", (id, ))
      db.commit()
    except:
      sys.stderr.write('Error in updating table ngrams of id %s\n' % (id))
      db.rollback()

def check_required_tables(db, cursor):
  required_tbls = ['authors', 'papers', 'ngrams']
  for tbl in required_tbls:
    if not is_tbl_exists(db, cursor, tbl):
      raise Exception('Table "' + tbl + '" does not exist in the specified table')

def gen_required_tables():
  os.system('./run_all.py --is_parse_wiki=False')

class TestChemSeers(unittest.TestCase):
  """Test ChemSeers expert recommendation system"""

  def get_experts_from_keywords(self, keyword):
    db, cursor = init_db()
    cursor.execute("""SELECT authors.name FROM authors, ngrams, personal_keywords """ + \
                   """WHERE ngrams.name=%s AND personal_keywords.ngram_id = ngrams.id """ + \
                   """AND authors.cluster=personal_keywords.person_cluster """ + \
                   """GROUP BY authors.name""", (keyword))
    rows = cursor.fetchall()
    close_db(db, cursor)
    return [r[0] for r in rows]

  def get_expertise_from_author(self, author):
    db, cursor = init_db()
    cursor.execute("""SELECT ngrams.name FROM ngrams, personal_keywords, authors """ + \
                   """WHERE ngrams.id=personal_keywords.ngram_id AND """ + \
                   """personal_keywords.person_cluster = authors.cluster AND """ + \
                   """ngrams.is_valid AND authors.name=%s GROUP BY ngrams.name""", (author))
    rows = cursor.fetchall()
    close_db(db, cursor)

    return [r[0] for r in rows]

  def setUp(self):
    pass

  def test_experts_of_keywords(self):
    keywords = ['nuclear physics', 'nuclear fusion', 'steel']
    experts = [['David Johnson', 'Helen Smith'], ['David Johnson', 'Peter Williams', 'Sean Jones'], ['Jenny Brown']]
    for i, keyword in enumerate(keywords):
      expert_list = self.get_experts_from_keywords(keyword)
      self.assertEqual(len(expert_list), len(experts[i]), msg="Wrong number of experts of topic '" + keyword + "'")
      for expert in expert_list:
        self.assertTrue(expert in experts[i], msg="'" + expert + "' is not an expert of '" + keyword + "'")

  def test_personal_expertise(self):
    authors = ['Jenny Brown', "Peter Williams"]
    expertises = [['chemical element', 'symbol', 'foo bar network', \
                   'elements', 'metal', 'alloy', 'vanadium', 'name', 'steel', \
                   'iron', 'chromium', 'carbon', 'melting', 'atomic number'], \
                  ['nuclear reaction', 'matter', 'mass', 'atomic nuclei', \
                   'nuclear fusion', 'energy']]
    for i, author in enumerate(authors):
      expertise_list = self.get_expertise_from_author(author)
      self.assertEqual(len(expertise_list), len(expertises[i]), \
                       msg="Wrong number of expertises for author '" + author + "'")
      for expertise in expertise_list:
        self.assertTrue(expertise in expertises[i], \
                        msg="'" + expertise + "' is not an expertise of author '" + author + "'")

  def test_personal_keywords_info(self):
    (count, log_cite_prod_count) = self.get_personal_keyword_info(1, 3274)
    self.assertEqual(count, 2)
    self.assertAlmostEqual(log_cite_prod_count, 3.48734)
    (count, log_cite_prod_count) = self.get_personal_keyword_info(2, 5850)
    self.assertEqual(count, 4)
    self.assertAlmostEqual(log_cite_prod_count, 12.4927)
    (count, log_cite_prod_count) = self.get_personal_keyword_info(2, 3119)
    self.assertEqual(count, 2)
    self.assertAlmostEqual(log_cite_prod_count, 5.08608)
    (count, log_cite_prod_count) = self.get_personal_keyword_info(3, 3119)
    self.assertEqual(count, 2)
    self.assertAlmostEqual(log_cite_prod_count, 5.08608)
    (count, log_cite_prod_count) = self.get_personal_keyword_info(4, 1192)
    self.assertEqual(count, 2)
    self.assertAlmostEqual(log_cite_prod_count, 4.58663)
    (count, log_cite_prod_count) = self.get_personal_keyword_info(5, 1492)
    self.assertEqual(count, 3)
    self.assertAlmostEqual(log_cite_prod_count, 4.65433)

  def get_personal_keyword_info(self, person_cluster, ngram_id):
    db, cursor = init_db()
    cursor.execute("""SELECT count, log_cite_prod_count FROM personal_keywords """ + \
                   """WHERE person_cluster = %s AND ngram_id = %s""", (person_cluster, ngram_id))
    row = cursor.fetchone()
    close_db(db, cursor)
    return row

  def get_ngram_co_occur_info(self, min_co_occur=1):
    db, cursor = init_db()
    cursor.execute("""SELECT src_id, tar_id FROM ngram_relations """ + \
                   """WHERE co_occur >= %s""", (min_co_occur))
    rows = cursor.fetchall()
    close_db(db, cursor)
    return [(r[0], r[1]) for r in rows]

  def test_ngram_relations(self):
    ngram_co_appear_info = self.get_ngram_co_occur_info(1)
    self.assertEqual(len(ngram_co_appear_info), 1398, \
                     msg="Incorrect number of rows in table ngram_relations")

    src_tar_co_occur_at_least_two = [(45355, 9043), (9043, 45355), (7561, 33552), \
                                     (7561, 4167), (7561, 985), \
                                     (33552, 4167), (33552, 985), (33552, 7561), \
                                     (4167, 33552), (4167, 985), (4167, 7561), \
                                     (985, 33552), (985, 4167), (985, 7561)]
    ngram_co_appear_info = self.get_ngram_co_occur_info(2)
    self.assertEqual(len(ngram_co_appear_info), len(src_tar_co_occur_at_least_two), \
                     msg="Incorrect number of rows in table ngram_relations")
    for src_tar_co_occur in src_tar_co_occur_at_least_two:
      self.assertTrue(src_tar_co_occur in ngram_co_appear_info, 
                      msg=str(src_tar_co_occur) + ' not in ngram_relations')

  def get_ngram_info(self, term):
    db, cursor = init_db()
    cursor.execute("""SELECT name, freq FROM ngrams WHERE name=%s""", (term))
    row = cursor.fetchone()
    close_db(db, cursor)
    return row

  def test_user_defined_terms(self):
    term = 'foo bar network'
    (name, freq) = self.get_ngram_info(term)
    self.assertEqual(name, term)
    self.assertEqual(freq, 1)

    term = 'qux baz analysis'
    (name, freq) = self.get_ngram_info(term)
    self.assertEqual(name, term)
    self.assertEqual(freq, 0)

    term = 'energy'
    (name, freq) = self.get_ngram_info(term)
    self.assertEqual(name, term)
    self.assertEqual(freq, 2)

    term = 'quux corge'
    (name, freq) = self.get_ngram_info(term)
    self.assertEqual(name, term)
    self.assertEqual(freq, 2)

def main(argv):
  database_reset_confirmation()

  # reset and generate necessary tables
  reset_tables()
  gen_required_tables()

  # perform testings
  suite = unittest.TestLoader().loadTestsFromTestCase(TestChemSeers)
  unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
  main(sys.argv)

