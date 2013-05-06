#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 18-09-2012
# Last Modified: Mon 06 May 2013 01:31:30 PM EDT

import codecs
import os
import sys
import wikitools

from mysql_util import init_db, close_db, is_db_exists, is_tbl_exists

site = wikitools.Wiki("http://en.wikipedia.org/w/api.php")

def usage(cmd):
  print 'Usage:', cmd
  return

def get_root_categories():
  root_categories = [ ]
  f = open('./settings/category_list', 'r')
  for line in f:
    line = line.strip().lower().split()
    if len(line) <= 1 or not line[-1].isdigit():
      raise Exception('Error in parsing "./settings/category_list"')
    root_categories.append((' '.join(line[0:-1]), int(line[-1])))
  f.close()
  return root_categories

def retrieve_pages_in_category(cate_title, typ):
  # Return: pages (type: dictionary, keys are integers, values are strings)
  # pages[pageid] = page_title
  # when typ == 'page': return only pages (not sub-categories);
  # when typ == 'subcat': return only sub-categories (not pages);
  # Ex: pages[5323] = 'Computer science' ==> by Wikipedia, the pageid of 'Computer science' is 5323

  assert(typ in ['page', 'subcat'])
  pages = { }
  category_prefix = 'category:'
  cate_title = category_prefix + cate_title \
      if cate_title[0:len(category_prefix)].lower() != category_prefix \
      else cate_title
  params = {'action': 'query', 'list': 'categorymembers', 'cmtype': typ, \
      'cmlimit': 500, # the maximum allowed return page number
      'cmtitle': cate_title, }
  req = wikitools.api.APIRequest(site, params)
  response = req.query(False)
  if 'query' in response:
    if 'categorymembers' in response['query']:
      for member in response['query']['categorymembers']:
        if 'pageid' in member and 'title' in member and member['title'][0:5].lower() != 'user:':
          pages[member['pageid']] = member['title']
  return pages

def get_wiki_page_id_by_title(title):
  p = wikitools.Page(site, title)
  if not p.exists:
    return -1
  return p.pageid

def insert_category(category_structure, cate_title, depth):
  category_prefix = 'category:'
  cate_title = category_prefix + cate_title \
      if cate_title[0:len(category_prefix)].lower() != category_prefix \
      else cate_title
  cate_id = get_wiki_page_id_by_title(cate_title)
  if cate_id == -1:
    return
  category_structure[cate_title] = { }
  if depth == 0:
    return
  sub_cate_info = retrieve_pages_in_category(cate_title, 'subcat')
  for sub_cate_title in sub_cate_info.values():
    insert_category(category_structure[cate_title], sub_cate_title, depth-1)

def get_category_structure(root_cate_title, depth):
  print 'Generating category structure'
  category_structure = { }
  insert_category(category_structure, root_cate_title, depth)
  return category_structure

def is_root_category_in_db(db, cursor, root_category):
  cursor.execute("""SELECT * FROM root_categories WHERE name=%s""", (root_category))
  row = cursor.fetchone()
  return row != None

def save_root_categories_to_db(root_categories):
  db, cursor = init_db()
  table_name = 'root_categories'
  if not is_tbl_exists(db, cursor, table_name):
    cursor.execute('CREATE TABLE ' + table_name + \
        ' (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ' + \
        ' name VARCHAR(100) NOT NULL)')
  for root_category in root_categories:
    if not is_root_category_in_db(db, cursor, root_category[0]):
      try:
        cursor.execute("""INSERT INTO root_categories (name) VALUES (%s)""", (root_category[0],))
      except Exception, e:
        print repr(e)
  close_db(db, cursor)

def iter_through_nested_dict_keys(di, li):
  for k in di.keys():
    li.append(k)
    if len(di[k]) > 0:
      iter_through_nested_dict_keys(di[k], li)

def nested_dict_keys_to_list(category_structure):
  category_list = [ ]
  iter_through_nested_dict_keys(category_structure, category_list)
  return sorted(list(set(category_list)))

def save_category_list(root_cate_title, categories, depth):
  category_output_dir = 'outputs/category'
  f = codecs.open(os.path.join(category_output_dir, \
      root_cate_title + '_depth_' + str(depth) + '_categories'), mode='w', encoding='utf-8')
  for category in categories:
    f.write(category + '\n')
  f.close()

def get_redirect_term(site, query_term):
  p = wikitools.Page(site, query_term)
  if not p.exists:
    return ''
  return p.title.lower()

def get_titles_from_categories(categories):
  print 'Generating seed keyphraes from each category...'
  pages = [ ]
  num_categories = len(categories)
  for i, category in enumerate(categories):
    sys.stdout.write('%d / %d : %s\n' % (i+1, num_categories, category.encode('utf-8')))
    pages.extend(retrieve_pages_in_category(category, typ='page').values())
  sys.stdout.write("\n")
  return sorted(list(set(pages)))

def remove_files_in_path(path):
  for f in os.listdir(path):
    os.remove(os.path.join(path, f))

def save_title_list(root_cate_title, titles, depth):
  title_output_dir = 'outputs/title'
  f = codecs.open(os.path.join(title_output_dir, \
      root_cate_title + '_depth_' + str(depth) + '_titles'), mode='w', encoding='utf-8')
  for title in titles:
    f.write(title + '\n')
  f.close()

def clean_output_folders():
  output_dirs = ['outputs/category', 'outputs/title']
  for output_dir in output_dirs:
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)
    remove_files_in_path(output_dir)

def main(argv):
  root_categories = get_root_categories()
  save_root_categories_to_db(root_categories)

  clean_output_folders()

  for i, (root_cate_title, depth) in enumerate(root_categories):
    print 'Processing root category "' + root_cate_title + \
        '": ' + str(i+1) + '/' + str(len(root_categories))
    category_structure = get_category_structure(root_cate_title, depth)
    categories = nested_dict_keys_to_list(category_structure)
    save_category_list(root_cate_title, categories, depth)
    titles = get_titles_from_categories(categories)
    save_title_list(root_cate_title, titles, depth)

if __name__ == "__main__":
  main(sys.argv)

# testing codes below
from nose.tools import assert_equal

class Tests():
  def test_is_db_exists(self):
    db, cursor = init_db()
    assert_equal(is_db_exists(db, cursor, 'this-is-a-not-existing-database'), False)
    assert_equal(is_db_exists(db, cursor, 'information_schema'), True)
    close_db(db, cursor)

  def test_retrieve_pages_in_category(self):
    root_category = 'computer science'
    pages = retrieve_pages_in_category(root_category, typ='page')
    assert_equal(pages, {33828320: u'Computational Advertising', 169633: u'Outline of computer science', 684709: u'Boyer\u2013Moore string search algorithm', 11037985: u'PGDCA', 5323: u'Computer science', 37340815: u'Access modifiers', 36685332: u'Department of Computer Science UBIT, University of Karachi', 25852537: u'Computer science in sport', 36776993: u'Software defined storage', 37081445: u'Soft state'})

    categories = retrieve_pages_in_category(root_category, typ='subcat')
    assert_equal(categories, {2977953: u'Category:Computer science conferences', \
        30730499: u'Category:History of computer science', \
        1866234: u'Category:Unsolved problems in computer science', \
        694790: u'Category:Computer scientists', 33240744: u'Category:Areas of computer science', \
        3179625: u'Category:Computer science literature', \
        2977994: u'Category:Computer science organizations', \
        27537394: u'Category:Wikipedia books on computer science', \
        1859318: u'Category:Computer science stubs', 2379705: u'Category:Computer science awards', \
        2275290: u'Category:Computer science education', \
        30759626: u'Category:Philosophy of computer science', 36544639: u'Category:Computer science portal'})

    root_category = 'chemistry'
    pages = retrieve_pages_in_category(root_category, typ='page')
    assert_equal(len(pages), 89)

  def test_get_category_structure(self):
    cate_title = 'computer science'
    cate_structure = get_category_structure(cate_title, 0)
    assert_equal(cate_structure, {'category:computer science': { }})
    cate_structure = get_category_structure(cate_title, 1)
    assert_equal(cate_structure, {'category:computer science': \
        {u'Category:Computer science awards': {}, u'Category:Computer science organizations': {}, \
        u'Category:Wikipedia books on computer science': {}, u'Category:Computer science education': {}, \
        u'Category:Unsolved problems in computer science': {}, \
        u'Category:Computer science conferences': {}, u'Category:Computer science literature': {}, \
        u'Category:History of computer science': {}, u'Category:Computer science portal': {}, \
        u'Category:Philosophy of computer science': {}, u'Category:Computer scientists': {}, \
        u'Category:Areas of computer science': {}, u'Category:Computer science stubs': {}}})
    cate_title = 'Computer science education'
    cate_structure = get_category_structure(cate_title, 2)
    assert_equal(cate_structure, \
        {'category:Computer science education': \
          {u'Category:Mathematics and Computing Colleges in England': \
            {u'Category:Mathematics and Computing Colleges in London': {}}, \
           u'Category:Computer science departments': \
            {u'Category:Computer science departments in the United States': {}, \
             u'Category:Computer science departments in the United Kingdom': {}, \
             u'Category:Computer science departments in Canada': {}}}})

  def test_nested_dict_keys_to_list(self):
    cate_title = 'Computer science education'
    cate_structure = get_category_structure(cate_title, 2)
    assert_equal(nested_dict_keys_to_list(cate_structure), \
         ['category:Computer science education', \
         u'Category:Mathematics and Computing Colleges in England', \
         u'Category:Mathematics and Computing Colleges in London', \
         u'Category:Computer science departments', \
         u'Category:Computer science departments in the United States', \
         u'Category:Computer science departments in the United Kingdom', \
         u'Category:Computer science departments in Canada'])

