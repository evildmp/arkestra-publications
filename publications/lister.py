from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from django_easyfilters.filters import ForeignKeyFilter

from arkestra_utilities.generic_lister import ArkestraGenericList, ArkestraGenericLister, ArkestraGenericFilterSet
from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE, MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH

from models import BibliographicRecord, Researcher, Authored

from datetime import datetime


class PublicationsGenericFilterSet(ArkestraGenericFilterSet):
    fields = [
        # ('authored__is_a_favourite', {}, ForeignKeyFilter), # won't work
        # "publication_date",
        ]

class PublicationsList(ArkestraGenericList):
    model = BibliographicRecord
    heading_text = _(u"Publications")
    item_template = "publications/publications_list_item.html"

    def set_items_for_context(self):
        start = datetime.now()
        # usually, the context for lists is the Entity we're publishing the
        # lists for, but this could be Place or Person for Events, for example
        # requires:     self.model.objects.listable_objects()
        # sets:         self.items_for_context

        entities = self.entity.get_real_ancestor.get_descendants(
            include_self=True
            ).values_list('id', flat=True)
        researchers = Researcher.objects.filter(
            person__member_of__entity__in=entities
            ).distinct().values_list('person', flat=True)

        if self.lister.favourites_only:
            filter_for_favourites = Q(authored__is_a_favourite=True)
        else:
            filter_for_favourites = Q()

        publications = BibliographicRecord.objects.filter(
            filter_for_favourites,
            authored__visible=True,
            authored__researcher__in=researchers,
            ).distinct().order_by('-publication_date')

        self.items_for_context = publications
        print publications.count(), datetime.now() - start

    def additional_list_processing(self):
        self.remove_expired()
        self.re_order_by_importance() # expensive; shame it has to be here
        self.truncate_items()
        self.set_show_when()

    def truncate_items(self):
        # we use our own truncate_items() because the one on the generic
        # plugin uses len(items)
        # acts on self.limit_to
        if self.items.count() > self.limit_to:
            self.items = self.items[:self.limit_to]

    def other_items(self):
        other_items = []
        # test for the various other_item_kinds that might be needed here
        if "archived" in self.other_item_kinds:
            other_items.append({
                # where we'll find them
                "link": self.entity.get_auto_page_url("publications-archive"),
                # the link title
                "title": "Archived publications",
                # count them
                "count": self.items_for_context.count()
            })
        return other_items


class PublicationsListLatest(PublicationsList):
    other_item_kinds = ("archived",)


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

    def additional_list_processing(self):
        self.filter_on_search_terms()
        self.itemfilter = self.filter_set(self.items, self.request.GET)


class PublicationsSelectedListForPerson(PublicationsList):
    def set_items_for_context(self):
        self.items_for_context = BibliographicRecord.objects.filter(
            authored__visible=True,
            authored__is_a_favourite=True,
            authored__researcher=self.lister.researcher,
            ).distinct().order_by('-publication_date')[0:6]

    def other_items(self):
        other_items = []
        # test for the various other_item_kinds that might be needed here
        if "archived" in self.other_item_kinds:
            other_items.append({
                # where we'll find them
                "link": self.entity.get_auto_page_url("publications-archive"),
                # the link title
                "title": "Archived publications",
                # count them
                "count": self.items_for_context.count()
            })
        return other_items
        

class PublicationsArchiveListForPerson(PublicationsArchiveList):
    def set_items_for_context(self):
        self.items_for_context = BibliographicRecord.objects.filter(
            authored__visible=True,
            authored__researcher=self.lister.researcher,
            ).distinct().order_by('-publication_date')

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
    listkinds=[
        ("publications", PublicationsList),
            ]
    display = "publications"
    other_item_kinds = ("archived")


class PublicationsMenuLister(object):
    lists = True
    def __init__(self, **kwargs):
        pass
    # favourites_only = False
    # listkinds=[
    #     ("publications", PublicationsList),
    #         ]
    # display = "publications"
