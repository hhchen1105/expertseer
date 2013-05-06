# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

import math
import operator

from collections import defaultdict
from django.db import models, connection
from rel_keyphrases.models import Ngrams

class Authors(models.Model):
  id = models.IntegerField(primary_key=True)
  cluster = models.IntegerField(null=True, blank=True)
  name = models.CharField(max_length=300, blank=True)
  affil = models.CharField(max_length=765, blank=True)
  email = models.CharField(max_length=300, blank=True)
  paper_cluster = models.IntegerField(null=True, blank=True)
  class Meta:
    db_table = u'authors'

  def query_expertise(self, person_cluster_id, num_return=15):
    if num_return <= 0:
      return [ ]
    cursor = connection.cursor()
    cursor.execute("""SELECT ngrams.name, ngrams.freq FROM ngrams, personal_keywords WHERE person_cluster=%s AND ngrams.id=personal_keywords.ngram_id AND ngrams.is_valid ORDER BY log_cite_prod_count DESC LIMIT %s;""", [person_cluster_id, num_return])
    expertises = cursor.fetchall()
    return expertises

  def query_publications(self, person_cluster_id):
    cursor = connection.cursor()
    cursor.execute("""SELECT papers.title, papers.year, papers.ncites, papers.cluster, papers.pdf_url FROM papers, authors WHERE authors.cluster=%s AND authors.paper_cluster=papers.cluster ORDER BY papers.year DESC""", [person_cluster_id])
    publications = cursor.fetchall()
    return publications

class PersonalKeywords(models.Model):
  id = models.IntegerField(primary_key=True)
  person_cluster = models.IntegerField(null=True, blank=True)
  ngram_id = models.IntegerField(null=True, blank=True)
  year = models.IntegerField(null=True, blank=True)
  count = models.IntegerField(null=True, blank=True)
  class Meta:
    db_table = u'personal_keywords'

  def query_experts_by_paper_ids(self, paper_id_score_pairs, num_return=40):
    max_num_of_papers = 40
    paper_id_score_pairs = paper_id_score_pairs[:max_num_of_papers]
    ncites = [ ]
    authors = [ ]
    for (paper_id, paper_score) in paper_id_score_pairs:
      ncites.append(self._get_ncites_by_paper_cluster(paper_id))
      authors.append(self._get_authors_by_paper_cluster(paper_id))
    experts = defaultdict(float)
    for i, (paper_id, paper_score) in enumerate(paper_id_score_pairs):
      for author in authors[i]:
        experts[author] += paper_score * math.log(math.exp(1) + ncites[i])
    sorted_experts = sorted(experts.iteritems(), key=operator.itemgetter(1), reverse=True)
    return [author for (author,score) in sorted_experts]

  def _get_authors_by_paper_cluster(self, paper_id):
    cursor = connection.cursor()
    cursor.execute("""SELECT name, cluster, affil, email FROM authors WHERE paper_cluster=%s""", (paper_id))
    rows = cursor.fetchall()
    return rows

  def _get_ncites_by_paper_cluster(self, paper_id):
    cursor = connection.cursor()
    cursor.execute("""SELECT ncites FROM papers WHERE cluster=%s""", (paper_id))
    row = cursor.fetchone()
    return row[0]

  def query_experts_exact_match(self, term, num_return=100):
    experts = [ ]
    q_term_info = Ngrams.objects.filter(name=term).values('id', 'name', 'freq')
    if len(q_term_info) == 0:
        return [ ]
    if len(q_term_info) == 1:
      q_term_id = q_term_info[0]['id']
      experts = self._query_experts_by_term_id(q_term_id, num_return)
    return experts

  def query_experts(self, term, num_return=100):
    experts = [ ]
    q_term_info = Ngrams.objects.filter(name=term).values('id', 'name', 'freq')
    if len(q_term_info) == 0:
      q_term_info = Ngrams.objects.filter(name__contains=term).values('id', 'name', 'freq')
      if len(q_term_info) == 0:
        return [ ]
    if len(q_term_info) == 1:
      q_term_id = q_term_info[0]['id']
      experts = self._query_experts_by_term_id(q_term_id, num_return)
    else:
      # more than 1 matched terms.  what should we do?
      # TODO: ...
      pass
    return experts

  def _query_experts_by_term_id(self, q_term_id, num_return):
    if num_return <= 0:
      return [ ]
    cursor = connection.cursor()
    # TODO: this query seems to be slow.  Can we optimize it?
    cursor.execute("""SELECT distinct(authors.name) as name, authors.cluster, authors.affil, authors.email FROM authors, personal_keywords WHERE personal_keywords.person_cluster=authors.cluster AND personal_keywords.ngram_id=%s GROUP BY cluster ORDER BY personal_keywords.log_cite_prod_count DESC LIMIT %s""", [q_term_id, num_return])
    experts = cursor.fetchall()
    return experts

class Papers(models.Model):
  id = models.CharField(max_length=300, blank=True)
  cluster = models.BigIntegerField(null=True, blank=True)
  title = models.CharField(max_length=765, blank=True)
  abstract = models.TextField(blank=True)
  venue = models.CharField(max_length=765, blank=True)
  ncites = models.IntegerField(null=True, blank=True)
  year = models.IntegerField(null=True, blank=True)
  pdf_url = models.CharField(max_length=765, blank=True)
  class Meta:
    db_table = u'papers'

