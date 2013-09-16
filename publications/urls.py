from django.conf.urls.defaults import patterns, url
from django.views.generic.dates import ArchiveIndexView

from views import ArticleYearArchiveView
urlpatterns = patterns('',
    
    url(r'^(?P<year>\d{4})/$',
        ArticleYearArchiveView.as_view(),
        name="article_year_archive"),

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