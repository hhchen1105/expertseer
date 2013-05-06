#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 18-09-2012
# Last Modified: Wed 19 Dec 2012 02:33:39 PM EST

import codecs
import math
import os
import sys
import wikitools

from HTMLParser import HTMLParser

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
  query_terms = set()
  directory = 'outputs/title/'
  term_files = [filename for filename in os.listdir(directory) \
      if os.path.isfile(os.path.join(directory,filename))]
  for filename in term_files:
    f = codecs.open(os.path.join(directory, filename), mode='r', encoding='utf-8')
    for line in f:
      query_terms.add(line.strip().lower())
    f.close()
  return sorted(list(query_terms))

def wiki_query_context(site, query_term, intro_only = True):
  params = {'action':'query', 'titles':query_term, 'prop':'extracts', 'redirects':''}
  if intro_only:
    params['exintro'] = ''
  try:
    req = wikitools.api.APIRequest(site, params)
  except:
    return None
  response = req.query(False)
  pageid = int(response['query']['pages'].keys()[0])
  if pageid == -1:
    return None
  wikitext = strip_tags(response['query']['pages'][str(pageid)]['extract'])
  return wikitext.lower()

def wiki_query_links(site, query_term, intro_only=True):
  page_text_content = wiki_query_context(site, query_term, intro_only)
  p = wikitools.Page(site, query_term)
  links = [ ]
  if p.exists:
    links = p.getLinks()

  return_links = [ ]
  for link in links:
    link = link.lower()
    if link in page_text_content:
      return_links.append(link)
  return return_links

def wiki_query_redirect_term(site, query_term):
  p = wikitools.Page(site, query_term)
  if not p.exists:
    return ''
  return p.title.lower()

def ins_keyphrases(keyphrases, query_term, redirect_term, links):
  keyphrases.add(query_term)
  if redirect_term != query_term and redirect_term != '':
    keyphrases.add(redirect_term)
  for link in links:
    if link != '' and link[0:5] != 'user:':
      keyphrases.add(link)

def get_ngram_id_by_name(db, cursor, name):
  cursor.execute("""SELECT id FROM ngrams WHERE name=%s""", (name))
  row = cursor.fetchone()
  return row[0] if row is not None else None

def save_one_keyphrase_to_table(db, cursor, name ):
  try:
    cursor.execute("""INSERT INTO ngrams (name, n) VALUES (%s, %s)""", \
        (name, len(name.split()), ))
    db.commit()
  except:
    sys.stderr.write('Error in inserting table ngrams "' + name + '"\n')
    db.rollback()

def save_keyphrases_to_table(keyphrases):
  db, cursor = init_db()
  if not is_tbl_exists(db, cursor, 'ngrams'):
    cursor.execute('CREATE TABLE ngrams ' + \
                   '(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ' + \
                   'name varchar(255) NOT NULL UNIQUE, ' + \
                   'n INT DEFAULT 0, ' + \
                   'freq INT DEFAULT 0, ' + \
                   'is_valid int(1) DEFAULT 1)')
  for k in keyphrases:
    ngram_id = get_ngram_id_by_name(db, cursor, k)
    if ngram_id == None:
      save_one_keyphrase_to_table(db, cursor, k)
  close_db(db, cursor)

def get_wiki_freq_by_ngram_id(db, cursor, id):
  cursor.execute("""SELECT wiki_freq FROM ngrams WHERE id=%s""", (id))
  row = cursor.fetchone()
  if row == None:
    return None
  return row[0]

def pmi(x, y, xy):
  return math.log(float(xy)/(x*y))

def normalize(v, orig_min, orig_max, new_min, new_max):
  if not orig_min <= v <= orig_max:
    raise Exception("Error in normalize()")
  return new_min + (float(v) - orig_min) * (new_max - new_min) / (orig_max - orig_min)

def gen_keyphrase_info(query_terms):
  batch_save_size = 100
  site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")

  keyphrases = set()
  num_query_terms = len(query_terms)
  print 'Generating keyphrase information'
  for i, query_term in enumerate(query_terms):
    sys.stdout.write('%d/%d: %s\n' %(i+1, num_query_terms, query_term.encode('utf-8')))
    sys.stdout.flush()
    redirect_term = wiki_query_redirect_term(site, query_term)
    links = wiki_query_links(site, query_term, intro_only = True)
    ins_keyphrases(keyphrases, query_term, redirect_term, links)
    if (i+1) % batch_save_size == 0:
      save_keyphrases_to_table(keyphrases)
      keyphrases = set()
  save_keyphrases_to_table(keyphrases)

  sys.stdout.write("\nCreating indexes...\n")

def main(argv):
  query_terms = get_query_terms()
  gen_keyphrase_info(query_terms)

if __name__ == "__main__":
  main(sys.argv)


# testing codes below
from nose.tools import assert_equal

def test_wiki_query_context():
  query_term = 'Hydrogen peroxide'
  site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")
  content = wiki_query_context(site, query_term, intro_only = True)
  partial_return = 'Hydrogen peroxide (H2O2) is the simplest peroxide (a compound with an oxygen-oxygen single bond). It is also a strong oxidizer.'.lower()
  assert_equal(content[0:len(partial_return)], partial_return)

def test_wiki_redirect_content():
  query_term = 'H2O2'
  site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")
  content = wiki_query_context(site, query_term, intro_only = True)
  partial_return = 'Hydrogen peroxide (H2O2) is the simplest peroxide (a compound with an oxygen-oxygen single bond). It is also a strong oxidizer.'.lower()
  assert_equal(content[0:len(partial_return)], partial_return)

def test_wiki_not_exist_content():
  query_term = 'this is a non-exist term'
  site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")
  content = wiki_query_context(site, query_term, intro_only = True)
  assert_equal(content, None)

def test_wiki_query_links():
  query_term = 'Hydrogen peroxide'
  site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")
  links = wiki_query_links(site, query_term, intro_only = True)
  real_links = [u'propellant', u'rocket', u'peroxidase', u'aerobes', u'metabolism', u'bleach', u'oxidizer', u'oxygen', u'oxidative metabolism', u'liquid', u'water', u'ear', u'peroxide', u'enzyme', u'hydrogen', u'reactive oxygen species', u'catalase', u'single bond']
  assert_equal(len(links), len(real_links))
  for link in real_links:
    assert(link in links)

def test_wiki_redirect_links():
  query_term = 'H2O2'
  site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")
  links = wiki_query_links(site, query_term, intro_only = True)
  real_links = [u'propellant', u'rocket', u'peroxidase', u'aerobes', u'metabolism', u'bleach', u'oxidizer', u'oxygen', u'oxidative metabolism', u'liquid', u'water', u'ear', u'peroxide', u'enzyme', u'hydrogen', u'reactive oxygen species', u'catalase', u'single bond']
  assert_equal(len(links), len(real_links))
  for link in real_links:
    assert(link in links)

def test_wiki_not_exist_link():
  query_term = 'this is a non-exist term'
  site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")
  links = wiki_query_links(site, query_term, intro_only = True)
  real_links = [ ]
  assert_equal(len(links), len(real_links))
  for link in real_links:
    assert(link in links)

def test_wiki_not_redirect():
  query_term = 'hydrogen peroxide'
  site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")
  redirect_term = wiki_query_redirect_term(site, query_term)
  assert_equal(query_term, redirect_term)

def test_wiki_does_redirect():
  query_term = 'h2o2'
  site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")
  redirect_term = wiki_query_redirect_term(site, query_term)
  assert_equal('hydrogen peroxide', redirect_term)

def test_wiki_not_exist_redirect():
  query_term = 'this is a non-exist term'
  site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")
  redirect_term = wiki_query_redirect_term(site, query_term)
  assert_equal('', redirect_term)

