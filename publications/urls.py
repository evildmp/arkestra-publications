from django.conf.urls.defaults import patterns, url, include

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

    url(
        r"^upload/$", views.upload, name="upload"),

    url(r'^publications-autocomplete/', include('autocomplete_light.urls')),
)