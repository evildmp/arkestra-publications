from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    
    # named entities' publications
    (r"^publications/(?P<slug>[-\w]+)/$", "publications.views.publications"),
    (r'^publications-archive/(?P<slug>[-\w]+)/$', "publications.views.publications_archive"),

    # base entity's publications
    (r'^publications/$', "publications.views.publications"),    
    (r'^publications-archive/$', "publications.views.publications_archive"),
)  