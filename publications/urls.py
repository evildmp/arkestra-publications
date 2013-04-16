from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    
    url(r"^publications/(?:(?P<slug>[-\w]+)/)?$", "publications.views.publications", name="publications"),
    url(r"^publications-archive/(?:(?P<slug>[-\w]+)/)?$", "publications.views.publications_archive", name="publications_archive"),

    # # named entities' publications
    # (r"^publications/(?P<slug>[-\w]+)/$", "publications.views.publications"),
    # (r'^publications-archive/(?P<slug>[-\w]+)/$', "publications.views.publications_archive"),
    # 
    # # base entity's publications
    # (r'^publications/$', "publications.views.publications"),    
    # (r'^publications-archive/$', "publications.views.publications_archive"),
)  