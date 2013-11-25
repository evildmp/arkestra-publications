# coding=utf-8

from datetime import datetime, timedelta

from django.test import TestCase
from django.test.utils import override_settings
from django.utils.encoding import force_unicode
from django.test.client import Client

from cms.models.placeholdermodel import Placeholder
from cms.api import add_plugin, create_page

from .models import (
    Researcher, Publication, BibliographicRecord, Authored
    )
from .lister import (
    PublicationsList, PublicationsLister, PublicationsListPlugin
    )

from contacts_and_people.models import Person, Entity, Membership


class ResearcherTests(TestCase):
    def test_methods(self):
        smith = Person(given_name=u"Zöe")
        researcher = Researcher(person=smith)
        force_unicode(researcher)
        self.assertEquals(force_unicode(researcher), researcher.__unicode__())
        smith.save()
        smith.delete()


class BibliographicRecordTests(TestCase):
    def test_copes_with_null_start_date(self):
        b = BibliographicRecord()
        self.assertEqual(b.get_start_date(), "")

    def test_copes_with_null_publication_date(self):
        b = BibliographicRecord()
        self.assertEqual(b.get_publication_date(), "")


@override_settings(CMS_TEMPLATES=(('null.html', "Null"),))
class PublicationsEntityPagesViewsTests(TestCase):
    urls = 'publications.test_urls'

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        home_page = create_page(
            title="test", template="null.html", language="en", published=True
            )

        self.school = Entity(
            name="School of Medicine",
            slug="medicine",
            auto_publications_page=True,
            website=home_page
            )

    # entity publications URLs - Entity.website published
    def test_main_url(self):
        self.school.save()
        response = self.client.get('/publications/')
        self.assertEqual(response.status_code, 200)

    def test_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_bogus_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_main_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/')
        self.assertEqual(response.status_code, 200)

    def test_entity_publications_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/medicine/')
        self.assertEqual(response.status_code, 200)

    def test_bogus_entity_publications_archive_url(self):
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
    def test_page_unpublished_main_url(self):
        self.school.save()
        response = self.client.get('/publications/')
        self.assertEqual(response.status_code, 404)

    def test_page_unpublished_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_page_unpublished_bogus_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_page_unpublished_main_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/')
        self.assertEqual(response.status_code, 404)

    def test_page_unpublished_entity_publications_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_page_unpublished_bogus_entity_publications_archive_url(self):
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
    def test_no_auto_page_main_url(self):
        self.school.save()
        response = self.client.get('/publications/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_bogus_entity_url(self):
        self.school.save()
        response = self.client.get('/publications/xxxx/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_main_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_entity_publications_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/medicine/')
        self.assertEqual(response.status_code, 404)

    def test_no_auto_page_bogus_entity_publications_archive_url(self):
        self.school.save()
        response = self.client.get('/publications-archive/xxxx/')
        self.assertEqual(response.status_code, 404)


class PublicationsModelBasicTests(TestCase):
    def setUp(self):
        p1 = Publication(guid="test-publication-1")
        p1.save()
        self.br1 = BibliographicRecord(
            publication=p1,
            publication_date=datetime.now()-timedelta(days=10)
            )
        self.br1.save()

        p = Person()
        p.save()
        r = Researcher(person=p)
        r.save()

        a1 = Authored(
            publication=p1,
            bibliographic_record=self.br1,
            researcher=r,
            visible=True
            )
        a1.save()

        p2 = Publication(guid="test-publication-2")
        p2.save()
        self.br2 = BibliographicRecord(
            publication=p2,
            publication_date=datetime.now()-timedelta(days=20)
            )
        self.br2.save()



    def test_save_and_find_bibliographic_record(self):
        self.assertItemsEqual(
            BibliographicRecord.objects.all(),
            [self.br1, self.br2]
            )

    def test_listable_objects(self):
        self.assertItemsEqual(
            BibliographicRecord.objects.listable_objects(),
            [self.br1]
        )



class PublicationsListTestsMixin(TestCase):
    def setUp(self):
        p1 = Publication(guid="test-publication-1")
        p1.save()
        self.br1 = BibliographicRecord(
            publication=p1,
            publication_date=datetime.now()-timedelta(days=10)
            )
        self.br1.save()

        p2 = Publication(guid="test-publication-2")
        p2.save()
        self.br2 = BibliographicRecord(
            publication=p2,
            publication_date=datetime.now()-timedelta(days=20)
            )
        self.br2.save()

        e = Entity()
        e.save()

        p = Person()
        p.save()

        m = Membership(
            person=p,
            entity=e
            )
        m.save()

        r = Researcher(person=p)
        r.save()

        a2 = Authored(
            is_a_favourite=True, publication=p2, researcher=r,
            bibliographic_record=self.br2, visible=True
            )
        a2.save()

        self.itemlist = PublicationsList()
        self.itemlist.items = BibliographicRecord.objects.all()
        self.e = e


class PublicationsListTests(PublicationsListTestsMixin):
    def test_list_items(self):
        self.assertEqual(
            list(self.itemlist.items),
            [self.br1, self.br2]
            )

    def test_favourites_only(self):
        self.itemlist.favourites_only = True
        self.itemlist.select_favourites()
        self.assertEqual(
            list(self.itemlist.items),
            [self.br2]
            )

    def test_items_for_entity(self):
        self.itemlist.entity = self.e
        self.itemlist.set_items_for_entity()
        self.assertEqual(
            list(self.itemlist.items),
            [self.br2]
            )

    def test_other_items(self):
        self.itemlist.entity = self.e
        self.itemlist.limit_to = 2
        self.itemlist.other_item_kinds = ["archived"]
        # make it thnk that there are 2 archived_items
        self.itemlist.archived_items = self.itemlist.items
        self.assertEqual(
            self.itemlist.other_items(),
            [{
                'count': 2,
                'link': '/publications-archive/',
                'title': 'Archived publications'
            }]
        )

class PluginTests(TestCase):
    def setUp(self):

        p1 = Publication(guid="test-publication-1")
        p1.save()
        self.br1 = BibliographicRecord(
            publication=p1,
            publication_date=datetime.now()-timedelta(days=10)
            )
        self.br1.save()

        p2 = Publication(guid="test-publication-2")
        p2.save()
        self.br2 = BibliographicRecord(
            publication=p2,
            publication_date=datetime.now()-timedelta(days=20)
            )
        self.br2.save()

        e = Entity()
        e.save()

        p = Person()
        p.save()

        m = Membership(
            person=p,
            entity=e
            )
        m.save()

        r = Researcher(person=p)
        r.save()

        a2 = Authored(
            is_a_favourite=True, publication=p2, researcher=r,
            bibliographic_record=self.br2
            )
        a2.save()

        self.itemlist = PublicationsList()
        self.itemlist.items = BibliographicRecord.objects.all()

        self.ph = Placeholder(slot=u"some_slot")
        self.ph.save()
        self.pl = add_plugin(
            self.ph,
            u"CMSPublicationsPlugin",
            u"en",
            entity=e
            )
        self.pl.save()

    def test_context_contains_a_lister(self):
        pp = self.pl.get_plugin_instance()[1]
        context = pp.render({}, self.pl, self.ph)
        self.assertIsInstance(context["lister"], PublicationsLister)
        self.assertIsInstance(
            context["lister"].lists[0],
            PublicationsListPlugin
            )


class PublicationsListerTests(PublicationsListTestsMixin):
    def test_lister_gets_an_item(self):
        self.assertEqual(
            set(PublicationsLister(entity=self.e).lists[0].items),
            set([self.br2])
            )
