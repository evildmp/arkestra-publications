from django.utils.translation import ugettext_lazy as _

from arkestra_utilities.generic_lister import ArkestraGenericList
from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE

from models import BibliographicRecord

class PublicationsList(ArkestraGenericList):
    model = BibliographicRecord
    heading_text = _(u"Publications")

    def set_items_for_context(self):
        # usually, the context for lists is the Entity we're publishing the
        # lists for, but this could be Place or Person for Events, for example
        # takes:    self.model.objects.listable_objects()
        # sets:     self.items_for_context
        self.items_for_context = self.model.objects.all()
        # if MULTIPLE_ENTITY_MODE and self.entity:
        #     self.items_for_context = items_for_context().filter(
        #         Q(hosted_by=self.entity) | Q(publish_to=self.entity)
        #         ).distinct()
