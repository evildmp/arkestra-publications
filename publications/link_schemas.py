from django.utils.encoding import smart_unicode

from easy_thumbnails.files import get_thumbnailer

from widgetry.views import search, SearchItemWrapper

from links import schema, LinkWrapper

from .models import (
    BibliographicRecord, publication_kinds, Researcher, Student, Supervisor
    )
from .admin import ResearcherAdmin, SupervisionInline


class BibliographicRecordWrapper(LinkWrapper):
    search_fields = ["title", "authors"]
    block_level_item_template = "publications/publications_list_item.html"
    special_attributes = [
        "authors",
        "journal",
        "template",
        "kind",
        "volume",
        "issue",
        "get_publication_date",
        "begin_page",
        "end_page",
        "edition",
        "editors",
        "first_author",
        "publisher",
        "get_publication_date",
        "get_start_date",
        "get_finish_date",
        "place_of_publication",
        "abstract"
        ]
    link_format_choices = (
        (u"title", u"Title only"),
        (u"details", u"Details"),
        (u"details kind", u"Details including kind"),
        )

    def template(self):
        return self.obj.template()

    def kind(self):
        return self.obj.kind()

    def url(self):
        return self.obj.get_absolute_url() or "No URL available"

    def get_absolute_url(self):
        return self.obj.get_absolute_url()

    def admin_metadata(self):
        kind = publication_kinds[self.obj.publication.type]

        if self.obj.publication.type in [
            "journal-article", "conference-proceeding", "other"
        ]:
            return "%s in %s, %s" % (
                kind,
                self.obj.journal,
                self.obj.get_publication_date(),
                )

        elif self.obj.publication.type in ["book", "chapter"]:
            return "%s, published %s<br>%s" % (
                kind,
                self.obj.get_publication_date(),
                self.obj.authors,
                )

        elif self.obj.publication.type in [
            "internet-publication", "patent", "report"
        ]:
            return "%s, %s<br>%s" % (
                kind,
                self.obj.get_publication_date(),
                self.obj.authors,
                )

        return publication_kinds[self.obj.publication.type]

    def authors(self):
        return self.obj.authors

    def journal(self):
        return self.obj.journal

    def volume(self):
        return self.obj.volume

    def issue(self):
        return self.obj.issue

    def get_publication_date(self):
        return self.obj.get_publication_date()

    def begin_page(self):
        return self.obj.begin_page

    def end_page(self):
        return self.obj.end_page

    def edition(self):
        return self.obj.edition

    def editors(self):
        return self.obj.editors

    def first_author(self):
        return self.obj.first_author

    def publisher(self):
        return self.obj.publisher

    def get_start_date(self):
        return self.obj.get_start_date()

    def get_finish_date(self):
        return self.obj.get_finish_date()

    def place_of_publication(self):
        return self.obj.place_of_publication

    def abstract(self):
        return self.obj.abstract


schema.register_wrapper(BibliographicRecord, BibliographicRecordWrapper)


class ResearcherWrapper(SearchItemWrapper):
    search_fields = ResearcherAdmin.search_fields

    def summary(self):
        data = []
        data.append(smart_unicode(self.obj.person.get_role))
        data.append(smart_unicode(self.obj.person.get_entity))
        return ', '.join(data)

    def thumbnail_url(self):
        try:
            size = self.THUMBNAIL_SIZE
            source = self.obj.person.image.file
            return get_thumbnailer(source).get_thumbnail({
                'subject_location': u'',
                'upscale': True,
                'crop': True,
                'size': (size, size)
            }).url
        except Exception, e:
            print "Error in personwrapper", e
            url = None
        return url

    def image(self):
        return self.obj.person.image


search.register_wrapper(Researcher, ResearcherWrapper)


class StudentWrapper(SearchItemWrapper):
    search_fields = SupervisionInline.search_fields

    def summary(self):
        data = []
        data.append(smart_unicode(self.obj.researcher.person.get_role))
        data.append(smart_unicode(self.obj.researcher.person.get_entity))
        return ', '.join(data)

    def thumbnail_url(self):
        try:
            size = self.THUMBNAIL_SIZE
            source = self.obj.researcher.person.image.file
            return get_thumbnailer(source).get_thumbnail({
                'subject_location': u'',
                'upscale': True,
                'crop': True,
                'size': (size, size)
            }).url
        except Exception, e:
            print "Error in personwrapper", e
            url = None
        return url

    def image(self):
        return self.obj.researcher.person.image

# registered with search, not schema: we want autocomplete, not links
search.register_wrapper(Student, StudentWrapper)
search.register_wrapper(Supervisor, StudentWrapper)
