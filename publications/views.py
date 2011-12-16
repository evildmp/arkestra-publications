from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.template import RequestContext

from contacts_and_people.models import Entity, default_entity

MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH = settings.MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
IN_BODY_HEADING_LEVEL = settings.IN_BODY_HEADING_LEVEL  

from arkestra_utilities.generic_models import ArkestraGenericPlugin
from cms_plugins import CMSPublicationsPlugin


def common_settings(request, slug):
    entity = Entity.objects.get(slug=slug) or default_entity
    request.auto_page_url = request.path
    # request.path = entity.get_website.get_absolute_url() # for the menu, so it knows where we are
    request.current_page = entity.get_website
    context = RequestContext(request)
    instance = ArkestraGenericPlugin()
    instance.limit_to = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
    instance.default_limit = MAIN_NEWS_EVENTS_PAGE_LIST_LENGTH
    instance.order_by = "importance/date"
    instance.entity = entity
    instance.heading_level = IN_BODY_HEADING_LEVEL
    instance.display = "news-and-events"
    instance.format = "details image"
    instance.view = "current"
    instance.main_page_body_file = "publications/publications.html"
    return instance, context, entity


def publications(request, slug=getattr(default_entity, "slug", None)):
    instance, context, entity = common_settings(request, slug)    

    instance.type = "main_page"
    instance.limit_to = 10
    meta = {"description": "Recent academic research publications",}
    title = str(entity)  + " recent publications"
    pagetitle = "Recent publications"
    
    CMSPublicationsPlugin().render(context, instance, None)
    
    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,
        }
        )
    
    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )

def publications_archive(request, slug=getattr(default_entity,"slug", None)):
    instance, context, entity = common_settings(request, slug)

    instance.type = "sub_page"
    instance.view = "archive"
    instance.display = "publications"
    instance.limit_to = None
    instance.order_by = "date"

    CMSPublicationsPlugin().render(context, instance, None)

    meta = {"description": "Archive of publications",}
    title = str(entity)  + " - publications archive"
    pagetitle = str(entity) + " - publications archive"

    context.update({
        "entity":entity,
        "title": title,
        "meta": meta,
        "pagetitle": pagetitle,
        "main_page_body_file": instance.main_page_body_file,
        'everything': instance,}
        )
    
    return render_to_response(
        "contacts_and_people/entity_information.html",
        context,
        )
