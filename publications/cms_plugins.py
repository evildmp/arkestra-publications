from django import forms
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core.cache import cache
from django.conf import settings

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from arkestra_utilities.generic_models import ArkestraGenericPlugin, ArkestraGenericPluginForm
from arkestra_utilities.admin_mixins import AutocompleteMixin

from contacts_and_people.templatetags.entity_tags import work_out_entity

from models import PublicationsPlugin, BibliographicRecord, PublicationsPlugin
from menu import menu_dict

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

class CMSPublicationsPlugin(ArkestraGenericPlugin, CMSPluginBase):
    name = _("Publications")
    model = PublicationsPlugin
    render_template = "publications/publications.html"
    # grab and use the menu_dict
    menu_cues = menu_dict

    # autocomplete fields
    related_search_fields = ['entity',]

    # render() runs the methods below in order
    
    def set_defaults(self, instance):
        # set defaults
        # ** important ** - these are set only when the render() function is called
        instance.favourites_only = getattr(instance, "favourites_only", False)
        instance.display = getattr(instance, "display", "publications")
        instance.list_format = "vertical"
        super(CMSPublicationsPlugin, self).set_defaults(instance)
        return

    def get_items(self, instance):
        start = datetime.now()
        super(CMSPublicationsPlugin, self).get_items(instance)
        
        # work out real entity
        if instance.entity.abstract_entity:
            instance.real_entity = instance.entity.get_real_ancestor()
        else: 
            instance.real_entity = instance.entity

        # create the publications dictionary
        publications = {}

        # tell it what its other_links method is called
        publications["links_to_other_items"] = self.other_links        
        
        # get the heading text from the plugin if supplied
        publications["heading_text"] = getattr(instance, "publications_heading_text", "Publications")
  
        # when running as type "menu", don't trouble the database - it takes too long
        if instance.type == "menu":
            publications["items"] = True
            instance.more_publications = True # for the other_links method             

        else:
            key = str(instance.real_entity.slug) + str(instance.view) + str(instance.type)
            cached = cache.get(key, None)
            if cached: 
                [publications["items"], publications["all_items_count"], instance.more_publications] = cached
            else:

                # get all publications
                all_publications = BibliographicRecord.objects.filter(
                    authored__visible = True,
                    authored__researcher__person__member_of__entity__in=instance.real_entity.get_descendants(include_self=True)) \
                    .distinct().order_by('-publication_date')

                # if an archive, get all ordered by kind 
                if instance.view == "archive":
                
                    # order them by type (article, book, etc)
                    ordered_publications = []    
                    for information in PUBLICATION_INFORMATION:
                        publication_type = information['type'] # because we cant use information['type'] inside a .filter()
                        pubs = all_publications.filter(publication__type = publication_type).order_by('-publication_date',)
                        for publication in pubs:
                            publication.kind = information['name']
                            ordered_publications.append(publication)    
                    pubs = ordered_publications

                elif instance.type == "main_page" or instance.favourites_only:
                    pubs = all_publications.filter(authored__is_a_favourite = True)[0:instance.limit_to]
            
                # set the more_publications flag 
                if instance.real_entity.website and all_publications.count() > instance.limit_to:
                    instance.more_publications = instance.real_entity.get_related_info_page_url("publications")
                else:
                    instance.more_publications = False
                
                cache.set(key, [pubs, all_publications.count(), instance.more_publications], settings.PUBLICATIONS_CACHE_DURATION, 60 * 60 * 6)

                publications["items"] = pubs
                publications["all_items_count"] = all_publications.count()
    
        self.lists = [publications,]
        print "get_items", datetime.now() - start
        
    # called by add_links_to_other_items()
    def other_links(self, instance, this_list):
        start = datetime.now()
        this_list["other_items"] = []
        if this_list["items"] and instance.view == "current":
            if instance.more_publications:
                this_list["other_items"] = [{
                    "link":instance.entity.get_related_info_page_url("publications-archive"), 
                    "title":"Publications archive",
                    "count": this_list.get("all_items_count"),
                    }]


        print "other_links", datetime.now() - start

    def set_limits_and_indexes(self, instance):
        start = datetime.now()
        for this_list in self.lists:
            # extract a list of dates for the index
            this_list["no_of_get_whens"] = len(set(getattr(item, "get_when", None) for item in this_list["items"]))
            # more than one date in the list: show an index
            if instance.view == "archive" and this_list["no_of_get_whens"] > 1:
                this_list["index"] = True
        print "set_limits_and_indexes", datetime.now() - start

    def icon_src(self, instance):
        return "/static/plugin_icons/publications_plugin.png"   



plugin_pool.register_plugin(CMSPublicationsPlugin)