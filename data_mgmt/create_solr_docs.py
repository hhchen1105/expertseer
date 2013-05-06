#!/usr/bin/env python

# Hung-Hsuan Chen <hhchen@psu.edu>
# Creation Date : 12-19-2012
# Last Modified: Mon 06 May 2013 01:30:33 PM EDT

import os
import sys

from lxml import etree
from mysql_util import init_db, close_db

def valid_XML_char_ordinal(i):
  return ( # conditions ordered by presumed frequency
      0x20 <= i <= 0xD7FF 
      or i in (0x9, 0xA, 0xD) 
      or 0xE000 <= i <= 0xFFFD 
      or 0x10000 <= i <= 0x10FFFF
  )

def assign_xml_node_text(node, text):
  try:
    node.text = text.decode('utf8') if text is not None else ''
  except:
    node.text = ''.join(c for c in text if valid_XML_char_ordinal(ord(c))).decode('utf8')

def create_solr_doc_files():
  batchsize = 100000
  solr_file_foler = "./settings/solr_files"
  db, cursor = init_db()
  print 'Querying paper contents'
  cursor.execute("""SELECT cluster, title, abstract, ncites FROM papers""")

  num_files = 0
  while True:
    rows = cursor.fetchmany(batchsize)
    if not rows:
      break
    num_files += 1
    print 'Generating doc file number ' + str(num_files)
    root = etree.Element('add')
    num_docs_to_gen = len(rows)
    for i, r in enumerate(rows):
      sys.stdout.write("\r%d / %d, id: %s" % (i+1, num_docs_to_gen, r[0]))
      doc = etree.Element('doc')
      id = etree.Element("field", name="id")
      id.text = str(r[0])
      title = etree.Element("field", name="title")
      assign_xml_node_text(title, r[1])
      abs = etree.Element("field", name="abstract")
      assign_xml_node_text(abs, r[2])
      ncites = etree.Element("field", name="ncites")
      ncites.text = str(r[3]) if r[3] is not None else '0'
      doc.append(id)
      doc.append(title)
      doc.append(abs)
      doc.append(ncites)
      root.append(doc)
    print ''
    f = open(os.path.join(solr_file_foler, 'papers' + str(num_files) + '.xml'), 'w')
    tree = etree.ElementTree(root)
    tree.write(f, encoding='utf8', pretty_print=True)
    f.close()
  close_db(db, cursor)

def main(argv):
  create_solr_doc_files()

if __name__ == "__main__":
  main(sys.argv)

