# Create your views here.
import solr

from django import forms
from django.shortcuts import render_to_response
from rel_keyphrases.models import NgramRelations
from experts.models import PersonalKeywords, Authors

class RelKeyphraseQueryForm(forms.Form):
  q_term = forms.CharField(max_length=100)

def index(request):
  if request.method == 'GET':
    form = RelKeyphraseQueryForm(request.GET)
  else:
    form = RelKeyphraseQueryForm()

  #ranking_method = ['ntf',
  #    #'tf',
  #    ]
  c = {
    'form': form,
  #  'ranking_method': ranking_method,
  }
  return render_to_response('rel_keyphrases/index.djhtml', c)

def show(request):
  if request.method == 'GET':
    form = RelKeyphraseQueryForm(request.GET)
  else:
    form = RelKeyphraseQueryForm()

  #ranking_method = ['ntf',
  #    #'tf',
  #    ]
  q_term = request.GET['q_term']
  #rank_method = request.GET['ranking_method'] if request.GET['ranking_method'] in ranking_method else 'ntf'

  NgramRelation = NgramRelations()
  rel_keyphrases = NgramRelation.query_related_terms(q_term, rank='ntf')

  # MySQL based query
  PersonalKeyword = PersonalKeywords()
  experts = PersonalKeyword.query_experts_exact_match(q_term)

  if len(experts) == 0:
    # solr based fulltext query
    s = solr.SolrConnection('http://localhost:8983/solr')
    response = s.query(q_term)
    paper_id_score_pairs = [(hit['id'], hit['score']) for hit in response.results]
    PersonalKeyword = PersonalKeywords()
    experts = PersonalKeyword.query_experts_by_paper_ids(paper_id_score_pairs)

  c = {
    'form': form,
    #'ranking_method' : ranking_method,
    'rel_keyphrases': rel_keyphrases,
    'q_term': q_term,
    #'rank_method': rank_method,
    'experts': experts,
  }
  return render_to_response('rel_keyphrases/show.djhtml', c)

def author(request):
  if request.method == 'GET':
    form = RelKeyphraseQueryForm(request.GET)
  else:
    form = RelKeyphraseQueryForm()

  q_term = request.GET['q_term']
  cluster_id = request.GET['cid']

  author = Authors.objects.filter(cluster=cluster_id)
  authors = Authors()
  expertises = authors.query_expertise(cluster_id)
  papers = authors.query_publications(cluster_id)

  c = {
    'form': form,
    'q_term': q_term,
    'author': author,
    'expertises': expertises,
    'papers': papers,
  }
  return render_to_response('experts/author.djhtml', c)


