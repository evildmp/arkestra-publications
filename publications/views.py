from arkestra_utilities.views import ArkestraGenericView
from arkestra_utilities.generic_lister import ArkestraGenericLister
from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE

from lister import PublicationsLister, PublicationsArchiveList


class PublicationsView(ArkestraGenericView):
    # really could get this from menu_dict
    auto_page_attribute = "auto_publications_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()
        self.lister = PublicationsLister(
            entity=self.entity,
            request=self.request,
            favourites_only=True,
            limit_to=10,
            )

        self.main_page_body_file = "arkestra/generic_lister.html"
        self.meta = {"description": "Latest key publications"}
        self.title = unicode(self.entity) + u" latest publications"
        if MULTIPLE_ENTITY_MODE:
            self.pagetitle = unicode(self.entity) + u" latest publications"
        else:
            self.pagetitle = "Latest key publications"

        return self.response(request)


class PublicationsArchiveView(ArkestraGenericView):
    auto_page_attribute = "auto_publications_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = ArkestraGenericLister(
            entity=self.entity,
            request=self.request,
            favourites_only=False,
            listkinds=[("publications", PublicationsArchiveList)],
            display="publications"
            )

        self.main_page_body_file = "arkestra/generic_filter_list.html"
        self.meta = {"description": "Searchable archive of publications items"}
        self.title = u"Archive of publications for %s" % unicode(self.entity)
        self.pagetitle = u"Archive of publications for %s" % unicode(self.entity)
        return self.response(request)
