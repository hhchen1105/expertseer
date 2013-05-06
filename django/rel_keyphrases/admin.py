from django.contrib import admin
from rel_keyphrases.models import Ngrams, NgramRelations

admin.site.register(Ngrams)
admin.site.register(NgramRelations)
