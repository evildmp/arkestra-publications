from django.conf.urls.defaults import patterns, url

from publications import views

urlpatterns = patterns('',

    # # named entities' publications
    url(
        r"^publications/(?:(?P<slug>[-\w]+)/)?$",
        views.PublicationsView.as_view(),
        name="publications"
        ),

    url(
        r"^publications-archive/(?:(?P<slug>[-\w]+)/)?$",
        views.PublicationsArchiveView.as_view(),
        name="publications-archive"
        ),

    url(
        r"^publications-csvdump/(?P<year>\d{4})/$",
        views.csv_dump,
        name="publications-csvdump"
        ),
)