from django.conf.urls.defaults import patterns, url, include
from django.views.generic.dates import ArchiveIndexView

from views import ArticleYearArchiveView
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^admin/', include(admin.site.urls)),

    # named entities' publications
    (r"^publications/(?P<slug>[-\w]+)/$", "publications.views.publications"),
    (r'^publications-archive/(?P<slug>[-\w]+)/$', "publications.views.publications_archive"),
    
    # base entity's publications
    (r'^publications/$', "publications.views.publications"),    
    (r'^publications-archive/$', "publications.views.publications_archive"),

    url(r'^', include('cms.urls')),

)  
