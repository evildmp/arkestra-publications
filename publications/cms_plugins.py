from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import PublicationsPlugin, BibliographicRecord
from django.utils.translation import ugettext as _

from django.db.models import Q
import operator

from templatetags.publications_tags import PUBLICATION_INFORMATION
from contacts_and_people.templatetags.entity_tags import work_out_entity

class CMSPublicationsPlugin(CMSPluginBase):
    model = PublicationsPlugin
    name = _("Publications")
    render_template = "publications.html"
    text_enabled = True
    def render(self, context, instance, placeholder):
        print " ---------- rendering CMSPublicationsPlugin -------------"
        if instance.entity:
            print instance.entity
            entity = instance.entity
        else:
            entity = work_out_entity(context, None)
            print instance.entity

        if entity.abstract_entity:
            real_entity = entity.get_real_ancestor()
        else: 
            real_entity = entity
        print "entity:", entity, "real entity:", real_entity
        selected_publications = []
        format = instance.format
        max_items = instance.limit_to
        if instance.favourites_only:
            print "selected items only"
            all_publications = BibliographicRecord.objects.filter(
            authored__visible = True,
            authored__researcher__person__member_of__entity__in=real_entity.get_descendants(include_self=True), 
            authored__is_a_favourite = True) \
            .distinct() \
            .order_by('-publication_date')
        else:
            all_publications = BibliographicRecord.objects.filter(
            authored__visible = True,
            authored__researcher__person__member_of__entity__in=real_entity.get_descendants(include_self=True)) \
            .distinct() \
            .order_by('-publication_date')
        print len(all_publications), "publications found"
        """
        for information in PUBLICATION_INFORMATION:
            publication_type = information['type'] # because we want to use it a bit later
            publications = all_publications.filter(publication__type = publication_type)
            for publication in publications:
                publication.template = "includes/" + publication_type + ".html"
                selected_publications.append(publication)
        #selected_publications.sort(reverse = True, key=operator.attrgetter('publication_date'))
        #selected_publications.sort(key=lambda x: x[0].publication_date)
        """
        more_publications = False
        if len(all_publications) > max_items and (real_entity.website or instance.entity): # if there are more publications, and either we can find a website for a real entity, or we have specified an entity here
            more_publications = True        
            print "we need to show the more publications link"  
        if instance.more_publications_link and instance.more_publications_link.website:
                more_publications_link = instance.more_publications_link
        else:
            more_publications_link = False
        context.update({
            "selected_publications": all_publications[0:max_items],
            'heading_level': instance.heading_level,
            "heading": instance.publications_heading_text,
            "format": instance.get_format_display(),
            "entity": entity,
            "real_entity": real_entity,
            "more_publications": more_publications, 
            "more_publications_link": more_publications_link,
        })
        print "about to return from render of publications plugin"
        return context
    def icon_src(self, instance):
        print "getting icon image for links plugin"
        return "/media/arkestra/publications_plugin.png"


plugin_pool.register_plugin(CMSPublicationsPlugin)