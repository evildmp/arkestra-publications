from django.conf.urls.defaults import patterns, url, include

from django.contrib import admin

admin.autodiscover()

# from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r"", include("publications.urls")),
    url(r"", include("cms.urls")),
    )


# urlpatterns = patterns('',
#
#     url(r'^admin/', include(admin.site.urls)),
#
#     # named entities' publications
#     url(
#         r"^publications/(?P<slug>[-\w]+)/$",
#         "publications.views.publications",
#         name="publications"),
#
#     url(
#         r'^publications-archive/(?P<slug>[-\w]+)/$',
#         "publications.views.publications_archive",
#         name="publications-archive"
#         ),
#
#     # base entity's publications
#     url(
#         r'^publications/$',
#         "publications.views.publications",
#         name="publications-base"
#         ),
#
#     url(
#         r'^publications-archive/$',
#         "publications.views.publications_archive",
#         name="publications-archive-base"
#         ),
#
#     url(r'^', include('cms.urls')),
#
# )
