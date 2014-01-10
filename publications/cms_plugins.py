from django import forms
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core.cache import cache
from publications.settings import PUBLICATIONS_CACHE_DURATION

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from arkestra_utilities.generic_models import ArkestraGenericPlugin, ArkestraGenericPluginForm
from arkestra_utilities.admin_mixins import AutocompleteMixin
from arkestra_utilities.generic_lister import ArkestraGenericLister

from contacts_and_people.templatetags.entity_tags import work_out_entity

from models import PublicationsPlugin, BibliographicRecord, PublicationsPlugin
from menu import menu_dict
from .lister import PublicationsListLatest, PublicationsLister
from datetime import datetime

class PublicationsPluginForm(ArkestraGenericPluginForm, forms.ModelForm):
    pass


PUBLICATION_INFORMATION = (
    {
        "type": "journal-article",
        "kind": "articles",
        "name": "Articles",
        },{
        "type": "book",
        "kind": "books",
        "name": "Books",
        },{
        "type": "chapter",
        "kind": "chapters",
        "name": "Chapters",
        },{
        "type": "conference-proceeding",
        "kind": "conference-proceedings",
        "name": "Conference proceedings",
        },{
        "type": "monograph",
        "kind": "monographs",
        "name": "Monographs",
        },{
        "type": "report",
        "kind": "reports",
        "name": "Reports",
    },
  )


class CMSPublicationsPlugin(ArkestraGenericPlugin, AutocompleteMixin, CMSPluginBase):
    model = PublicationsPlugin
    name = _("Publications")
    menu_cues = menu_dict

    # autocomplete fields
    related_search_fields = ['entity',]

    def icon_src(self, instance):
        return "/static/plugin_icons/publications_plugin.png"

    def render(self, context, instance, placeholder):
        self.entity = getattr(instance, "entity", None) or \
            work_out_entity(context, None)

        self.lister = PublicationsLister(
            listkinds=[
                ("publications", PublicationsListLatest),
                ],
            entity=self.entity,
            limit_to=instance.limit_to,
            item_format=instance.format,
            favourites_only=instance.favourites_only,
            )

        context.update({
            'lister': self.lister,
            'placeholder': placeholder,
            })
        return context


plugin_pool.register_plugin(CMSPublicationsPlugin)
