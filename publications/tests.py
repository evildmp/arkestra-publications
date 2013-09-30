# coding=utf-8

from django.test import TestCase
from django.test.utils import override_settings
from django.utils.encoding import force_unicode
from django.test.client import Client

import unittest

from cms.models.placeholdermodel import Placeholder
from cms.api import add_plugin, create_page

from publications.models import Researcher, Publication, Authored, PublicationsPlugin, BibliographicRecord

from contacts_and_people.models import Person, Entity

class ResearcherTests(unittest.TestCase):
    def test_methods(self):
        smith = Person(given_name=u"Zöe")
        researcher = Researcher(person=smith)
        force_unicode(researcher)
        self.assertEquals(force_unicode(researcher), researcher.__unicode__())
        smith.save()
        smith.delete()

class PluginTests(TestCase):
    def setUp(self):
        self.school = Entity(
            name="School of Medicine",
            slug="medicine",
            )
        self.school.save()
        self.placeholder = Placeholder(slot=u"some_slot")
        self.placeholder.save()
        self.plugin = add_plugin(
            self.placeholder,
            u"CMSPublicationsPlugin",
            u"en",
            entity=self.school
        )
        self.plugin.save()

    def test_kind_none(self):
        instance = self.plugin.get_plugin_instance()[1]
        self.plugin.type = None
        self.plugin.view = "current"
        self.plugin.favourites_only = False
        instance.render()
        print instance.lister.lists


class BibliographicRecordTests(TestCase):
    def test_copes_with_null_start_date(self):
        b = BibliographicRecord()
        self.assertEqual(b.get_start_date(), "")

class BibliographicRecordTests(TestCase):
    def test_copes_with_null_publication_date(self):
        b = BibliographicRecord()
        self.assertEqual(b.get_publication_date(), "")


@override_settings(
    CMS_TEMPLATES = (('null.html', "Null"),)
)
class PublicationsEntityPagesViewsTests(TestCase):
    urls = 'publications.test_urls'

    def setUp(self):
        # Every test needs a client.
        self.client = Client()


        home_page = create_page(title="test", template="null.html", language="en", published=True)

        self.school = Entity(
            name="School of Medicine",
            slug="medicine",
            auto_publications_page=True,
            website=home_page
            )

    # entity publications URLs - Entity.website published
    def test_publications_main_url(self):
        self.school.save()
        response = self.client.get('/publications/')
        self.assertEqual(response.status_code, 200)

    def test_publications_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_publications_bogus_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_publications_main_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/')
        self.assertEqual(response.status_code, 200)

    def test_publications_entity_publications_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_publications_bogus_entity_publications_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

class PublicationsEntityPageIsUnpublishedViewsTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        self.school = Entity(
            name="School of Medicine",
            slug="medicine",
            auto_publications_page=True,
            )

    # entity publications URLs - Entity.website unpublished
    def test_publications_page_unpublished_main_url(self):
        self.school.save()
        response = self.client.get('/publications/')
        self.assertEqual(response.status_code, 404)

    def test_publications_page_unpublished_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_publications_page_unpublished_bogus_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_publications_page_unpublished_main_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/')
        self.assertEqual(response.status_code, 404)

    def test_publications_page_unpublished_entity_publications_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_publications_page_unpublished_bogus_entity_publications_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/xxxx/')
        self.assertEqual(response.status_code, 404)


class PublicationsEntityPagesNoAutoPageViewsTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        self.school = Entity(
            name="School of Medicine",
            slug="medicine",
            auto_publications_page=False,
            )

    # entity publications URLs - no publications pages
    def test_publications_no_auto_page_main_url(self):
        self.school.save()
        response = self.client.get('/publications/')
        self.assertEqual(response.status_code, 404)

    def test_publications_no_auto_page_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_publications_no_auto_page_bogus_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_publications_no_auto_page_main_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/')
        self.assertEqual(response.status_code, 404)

    def test_publications_no_auto_page_entity_publications_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_publications_no_auto_page_bogus_entity_publications_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/xxxx/')
        self.assertEqual(response.status_code, 404)

from lister import PublicationsList, PublicationsLister

class PublicationsListTests(TestCase):
    def test_list_gets_an_item(self):
        p = Publication(guid="test-publication-1")
        p.save()
        br = BibliographicRecord(publication=p)
        br.save()
        self.assertEqual(
            set(PublicationsList().items),
            set([br])
            )

class PublicationsListerTests(TestCase):
    def test_lister_gets_an_item(self):
        p = Publication(guid="test-publication-1")
        p.save()
        br = BibliographicRecord(publication=p)
        br.save()
        self.assertEqual(
            set(PublicationsLister().lists[0].items),
            set([br])
            )

