# coding=utf-8

from django.test import TestCase
from django.test.utils import override_settings
from django.utils.encoding import force_unicode

import unittest

from publications.models import Researcher
from contacts_and_people.models import Person

class ResearcherTests(unittest.TestCase):
    def test_methods(self):
        smith = Person(given_name=u"Zöe")

        researcher = Researcher(person=smith)

        
        test = researcher.__unicode__()
 
        force_unicode(test)
        
        unicode(researcher)