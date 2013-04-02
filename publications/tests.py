# coding=utf-8

from django.test import TestCase
from django.test.utils import override_settings
from django.utils.encoding import force_unicode

import unittest

from cms.models.placeholdermodel import Placeholder
from cms.api import add_plugin

from publications.models import Researcher, PublicationsPlugin
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
        instance.get_items(self.plugin)