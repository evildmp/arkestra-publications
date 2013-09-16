from django.utils.translation import ugettext_lazy as _

from arkestra_utilities.generic_lister import ArkestraGenericList

from models import BibliographicRecord

class PublicationsList(ArkestraGenericList):
    model = BibliographicRecord
    heading_text = _(u"Publications")
