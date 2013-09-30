from django.conf.urls.defaults import patterns, url
from publications import views

urlpatterns = patterns('',
    
    # # named entities' publications
    # url(
    #     r"^publications/(?:(?P<slug>[-\w]+)/)$", 
    #     "publications.views.publications",
    #     name="publications"),
    #     
    # url(
    #     r'^publications-archive/(?P<slug>[-\w]+)/$',
    #     "publications.views.publications_archive",
    #     name="publications-archive"
    #     ),
    
    # base entity's publications
    url(
        r'^publications/$', 
        views.PublicationsView.as_view(),
        {"slug": None},
        name="publications-base"
        ),    
        
    url(
        r'^publications-archive/$',
        views.PublicationsArchiveView.as_view(),
        {"slug": None},
        name="publications-archive-base"
        ),
)  