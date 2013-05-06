#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 12-19-2012
# Last Modified: Fri 03 May 2013 10:28:47 AM EDT

'''
hhchen:
1. I'm assuming the values of "ID" fields in the xml files are universally unique.
   If this assumption is not true, we'll need to modify some code segments.
2. I'm not sure about the meaning of some fields in the xml file, so I just ignore them.
   It should be very straightforward to add them if needed.
'''

import gflags
import os
import re
import sys

from lxml import etree
from mysql_util import init_db, close_db

FLAGS = gflags.FLAGS
gflags.DEFINE_string('schema_file', '', 'The xml schema file')
gflags.DEFINE_string('xml_dir', '', 'The directory containing all the XML files')

def usage(cmd):
  print 'Usage:', cmd, \
        '--xml_dir=DIR/TO/XML/FILES', \
        '--schema_file=PATH/TO/SCHEMA/FILE'
  return

def check_args(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError:
    print FLAGS

  if not os.path.isdir(FLAGS.xml_dir):
    usage(argv[0])
    raise Exception('--xml_dir must be a valid directory')

  if not os.path.isfile(FLAGS.schema_file):
    usage(argv[0])
    raise Exception('--schema_file must be a valid file')

def get_element_value(doc, label):
  if len(doc.xpath(label)) == 0:
    return ''
  if doc.xpath(label)[0].text is None:
    return ''
  return doc.xpath(label)[0].text

def get_max_author_cluster(db, cursor):
  cursor.execute("""SELECT max(cluster) FROM authors""")
  row = cursor.fetchone()
  if row[0] is None:
    return 0
  return row[0]

def get_author_cluster(db, cursor, author):
  cursor.execute("""SELECT cluster FROM authors WHERE name = %s""", (author))
  row = cursor.fetchone()
  if row is None:
    return get_max_author_cluster(db, cursor) + 1
  else:
    return row[0]

def insert_tables(db, cursor, id, title, authors, abs, url):
  try:
    cursor.execute("""INSERT INTO papers (cluster, title, abstract, pdf_url) """ +
        """VALUES (%s, %s, %s, %s)""", (id, title, abs, url))
    db.commit()
  except:
    sys.stderr.write('Error in inserting paper of ID %s to papers\n' % (str(id)))
    db.rollback()

  for author in authors:
    author_cluster = get_author_cluster(db, cursor, author)
    try:
      cursor.execute("""INSERT INTO authors (cluster, name, paper_cluster) """ +
          """VALUES (%s, %s, %s)""", (author_cluster, author, id))
      db.commit()
    except:
      sys.stderr.write('Error in inserting author %s of paper with ID %s\n' % (author, str(id)))
      db.rollback()

def remove_parenthesis(stri):
  return re.sub(r'\(.*?\)', '', stri)

def keep_letter_and_comma_only(stri):
  return re.sub(r'[^a-zA-Z\s,]', '', stri)

def clean_authors(authors):
  ret_authors = [ ]
  for author in authors:
    author = remove_parenthesis(author)
    author = keep_letter_and_comma_only(author)
    author.strip()
    if author:
      ret_authors.append(author)
  return ret_authors

def dow_xml_to_mysql():
  xmlschema_doc = etree.parse(FLAGS.schema_file)
  xmlschema = etree.XMLSchema(xmlschema_doc)

  db, cursor = init_db()
  for root, sub_folders, files in os.walk(FLAGS.xml_dir):
    for file in files:
      # recursively find xml files
      if os.path.splitext(file)[1] == '.xml':
        tree = etree.parse(os.path.join(root, file))

        # check schema
        if not xmlschema.validate(tree):
          raise Exception("Incorrect schema of xml file " + os.path.join(root, file))

        # parse xml
        for doc in tree.xpath('dbo_RICKMETADATA'):
          (id, title, authors, abs, url) = ('', '', [], '', '')
          id = get_element_value(doc, 'ID')
          title = ' '.join(get_element_value(doc, 'TITL').splitlines()).strip()
          authors = clean_authors(';'.join(get_element_value(doc, 'AUTH').splitlines()).split(';'))
          abs = ' '.join(get_element_value(doc, 'ABST').splitlines()).strip()
          url = get_element_value(doc, 'LINK')

          # save to mysql
          if id != '':
            insert_tables(db, cursor, id, title, authors, abs, url)

  close_db(db, cursor)

def main(argv):
  check_args(argv)
  dow_xml_to_mysql()

if __name__ == "__main__":
  main(sys.argv)

