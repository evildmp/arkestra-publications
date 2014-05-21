from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.core.cache import cache

from arkestra_utilities.generic_lister import (
    ArkestraGenericList, ArkestraGenericLister, ArkestraGenericFilterSet
    )
from arkestra_utilities.utilities import generate_key

from .models import BibliographicRecord, Researcher, Authored

class PublicationsGenericFilterSet(ArkestraGenericFilterSet):
    fields = [
        # 'publication'
        # ('authored__is_a_favourite', {}, ForeignKeyFilter),
        # won't work "publication_date",
        ]


class PublicationsList(ArkestraGenericList):
    model = BibliographicRecord
    heading_text = _(u"Publications")
    favourites_only = False
    item_template = "publications/publications_list_item.html"

    def build(self):
        self.items = self.model.objects.listable_objects()

    # def select_favourites(self):
    #     if self.favourites_only:
    #         self.items = self.items.filter(authored__is_a_favourite=True)

    def set_items_for_entity(self):
        # requires:     self.model.objects.listable_objects()
        # sets:         self.items

        # first we get the entities we care about
        entities = self.entity.get_descendants(
            include_self=True
            ).values_list('id', flat=True)

        # and from the entities the researchers
        researchers = set(Researcher.objects.filter(
            person__entities__in=entities
            ).values_list('person', flat=True))

        # -------- original solution -------

        # This should be the optimal solution, but with smaller
        # entities queries can take 29 seconds!

        # authoreds = Authored.objects.filter(
        #     researcher__in=researchers,
        #     visible=True,
        #     ).values_list('bibliographic_record', flat=True)
        #
        # # if self.favourites_only:
        # #     authoreds = authoreds.filter(is_a_favourite=True)
        #
        # self.items = BibliographicRecord.objects.filter(
        #         id__in=authoreds,
        #         ).distinct()


        # -------- coerced solution -------

        authoreds = list(
            Authored.objects.filter(
                researcher__in=researchers,
                visible=True,
                ).values_list('bibliographic_record', flat=True)
            )

        self.items = BibliographicRecord.objects.filter(
                id__in=authoreds,
                ).distinct()

        # -------- Ben's solution 1 -------

        # self.items = BibliographicRecord.objects.filter(
        #         publication__authored__researcher__in=researchers,
        #         ).distinct()


        # -------- Ben's solution 2 -------

        # self.items = BibliographicRecord.objects.filter(
        #         authored__researcher__in=researchers,
        #         ).distinct()

        if self.favourites_only:
            self.items = self.items.filter(authored__is_a_favourite=True)


    def set_items_for_person(self):
        # find the visible authoreds for the researcher
        authoreds = Authored.objects.filter(
            researcher=self.researcher,
            visible=True
            )

        # if necessary, get the favourites only
        if self.favourites_only:
            authoreds = authoreds.filter(is_a_favourite=True)

        # find the matching Bibliographic records
        self.items = BibliographicRecord.objects.filter(
                id__in=authoreds.values_list('bibliographic_record', flat=True),
                ).distinct()

    def truncate_items(self):
        # in some lists, we only ask for a certain number of items
        # acts on self.limit_to

        self.items = self.items[:self.limit_to]

    @cached_property
    def other_items(self):

        other_items = []
        # test for the various other_item_kinds that might be needed here
        if "archived" in self.other_item_kinds:
            # print "counting other items", self.__class__
            other_items.append({
                # where we'll find them
                "link": self.entity.get_auto_page_url(
                    "publications-archive"
                    ),
                # the link title
                "title": "Archive of publications",
                # count them
                "count": self.archived_items_count
            })

        return other_items

    def is_showable(self):
        return True


class PublicationsListLatest(PublicationsList):
    other_item_kinds = ("archived",)

    def build(self):
        key = generate_key(
            self.__class__,
            "build",
            self.entity.id,
            self.limit_to,
            self.favourites_only
            )
        values = cache.get(key)
        if not values:
            # print "failed to get cache for ", self.__class__, key

            self.items = self.model.objects.listable_objects()
            self.set_items_for_entity()
            self.archived_items_count = self.items.count()
            self.truncate_items()

            values = (self.items, self.archived_items_count)
            # print cache.set(key, values, 60 * 60 * 12)

        else:
            # print "got cache for ", self.__class__
            (self.items, self.archived_items_count) = values


class PublicationsListPlugin(PublicationsList):
    other_item_kinds = ("archived",)

    def build(self):
        # print "getting items for ", self.__class__
        self.items = self.model.objects.listable_objects()
        self.set_items_for_entity()
        self.archived_items = self.items
        self.truncate_items()


class PublicationsListForPerson(PublicationsList):
    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_person()
        self.archived_items = self.items
        self.truncate_items()


class PublicationsArchiveList(PublicationsList):
    filter_set = PublicationsGenericFilterSet
    search_fields = [
        {
            "field_name": "authors",
            "field_label": "Authors",
            "placeholder": "Search",
            "search_keys": [
                "authors__icontains",
                ],
            },
        {
            "field_name": "title",
            "field_label": "Title",
            "placeholder": "Search",
            "search_keys": [
                "title__icontains",
                ],
            },
        # can't be enabled until
        # https://github.com/evildmp/arkestra-publications/issues/9 is resolved
        # {
        #     "field_name": "keywords",
        #     "field_label": "Keywords",
        #     "placeholder": "Search",
        #     "search_keys": [
        #         "keywords__icontains",
        #         ],
        #     },
        ]

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_entity()
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET)


class PublicationsArchiveListForPerson(PublicationsArchiveList):

    def build(self):
        self.items = self.model.objects.listable_objects()
        self.set_items_for_person()
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET)

    search_fields = [
        {
            "field_name": "authors",
            "field_label": "Co-authors",
            "placeholder": "Search",
            "search_keys": [
                "authors__icontains",
                ],
            },
        {
            "field_name": "title",
            "field_label": "Title",
            "placeholder": "Search",
            "search_keys": [
                "title__icontains",
                ],
            },
        ]


class PublicationsLister(ArkestraGenericLister):
    listkinds = [
        ("publications", PublicationsListLatest),
        ]
    display = "publications"


class PublicationsMenuList(PublicationsList):


    def other_items(self):

        other_items = [{
            # where we'll find them
            "link": self.entity.get_auto_page_url(
                "publications-archive"
                ),
            # the link title
            "title": "Archive",
            }]

        return other_items

    def build(self):
        # if the Lister has lists, then the menu system will create a node
        # for it without actually having to calculate whether there are any
        # items in the lists
        self.items = True


class PublicationsMenuLister(ArkestraGenericLister):
    listkinds = [
        ("publications", PublicationsMenuList),
        ]
    display = "publications"
