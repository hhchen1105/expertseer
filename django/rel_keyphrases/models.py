# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Ngrams(models.Model):
  id = models.IntegerField(primary_key=True)
  name = models.CharField(max_length=255, unique=True)
  n = models.IntegerField(null=True, blank=True)
  freq = models.IntegerField(null=True, blank=True)
  is_valid = models.IntegerField(null=True, blank=True)
  class Meta:
    db_table = u'ngrams'

class NgramRelations(models.Model):
  id = models.IntegerField(primary_key=True)
  src_id = models.IntegerField()
  tar_id = models.IntegerField()
  co_occur = models.IntegerField(null=True, blank=True)
  co_occur_norm = models.FloatField(null=True, blank=True)
  is_valid = models.IntegerField(null=True, blank=True)
  class Meta:
    db_table = u'ngram_relations'

  def query_related_terms(self, term, num_return = 15, rank='ntf'):
    rel_terms = [ ]
    q_term_info = Ngrams.objects.filter(name=term).values('id', 'name', 'freq')
    if len(q_term_info) == 0: # perform fuzzy search
      s = term.split()
      for sub_ngram in [' '.join(s[i:i+j]) for j in range(len(s), 0, -1) for i in range(len(s)-j+1)]:
        q_term_info = Ngrams.objects.filter(name__icontains=sub_ngram).values('id', 'name', 'freq')
        if len(q_term_info) > 0:
          break
      else:
        return [ ]
    if len(q_term_info) == 1:
      q_term_id = q_term_info[0]['id']
      rel_terms = self._query_related_terms_by_id(q_term_id, num_return, rank)
    else:
      for term_info in q_term_info[0:num_return]:
        rel_terms.append([term_info['name'], term_info['freq'], term_info['name']])
      i = 0
      while len(self._uniqify(rel_terms)) < 15 and i < len(q_term_info):
        rel_terms.extend(self._query_related_terms_by_id(q_term_info[i]['id'], num_return - len(rel_terms), rank))
        i += 1
    return self._uniqify(rel_terms)

  def _query_related_terms_by_id(self, term_id, num_return, rank):
    if num_return <= 0:
      return [ ]
    rel_terms = [ ]
    if rank == 'tf':
      for ngram_info in NgramRelations.objects.raw('SELECT ngrams.* FROM ngrams, ngram_relations WHERE ngram_relations.src_id=%s AND ngram_relations.tar_id=ngrams.id AND ngrams.is_valid AND ngram_relations.is_valid ORDER BY ngram_relations.co_occur DESC LIMIT %s' , [term_id, num_return]):
        rel_terms.append([ngram_info.name, ngram_info.freq, ngram_info.name])
    else:
      for ngram_info in NgramRelations.objects.raw('SELECT ngrams.* FROM ngrams, ngram_relations WHERE ngram_relations.src_id=%s AND ngram_relations.tar_id=ngrams.id AND ngrams.is_valid AND ngram_relations.is_valid ORDER BY ngram_relations.co_occur_norm DESC LIMIT %s' , [term_id, num_return]):
        rel_terms.append([ngram_info.name, ngram_info.freq, ngram_info.name])
    return rel_terms

  def _uniqify(self, seq):
    seen = set()
    return [x for x in seq if x[0] not in seen and not seen.add(x[0])]

