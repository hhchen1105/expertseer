from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'expertseers.views.home', name='home'),
    # url(r'^expertseers/', include('expertseers.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # for all media
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # for expertseers
    url(r'^$', 'rel_keyphrases.views.index'),
    url(r'^experts/$', 'rel_keyphrases.views.index'),
    url(r'^experts/show', 'rel_keyphrases.views.show'),
    url(r'^experts/author', 'rel_keyphrases.views.author'),
)
