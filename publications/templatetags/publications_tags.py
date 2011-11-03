from django import template
from django.template.defaultfilters import join, date
from django.shortcuts import render_to_response
from publications.models import BibliographicRecord, publication_kinds
from datetime import datetime
from contacts_and_people.templatetags.entity_tags import work_out_entity

import operator


class publicationobject(object):
    pass


register = template.Library()

"""
type: the Symplectic publications type, also used for the included template name
kind: used in the template for identifying the type
name: the human-readable version of kind
'journal-article',
'book',
'chapter',
'conference-proceeding',
'patent'
'report'
'software'
'performance'
'composition'
'design'
'artefact'
'exhibition'
'other'
'internet-publication'
'scholarly-edition'
"""
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

@register.inclusion_tag('person_selected_publications.html', takes_context = True)
def get_selected_person_publications(context, researcher = None):
    """   
    Lists Researcher's selected articles
    """
    selected_publications = []
    if researcher == None:
        researcher = context.get('person').researcher
    all_publications = BibliographicRecord.objects.filter(authored__visible = True, authored__researcher = researcher, authored__is_a_favourite = True)
    # loop first through the PUBLICATION_INFORMATION dictionaries
    for information in PUBLICATION_INFORMATION:
        publication_type = information['type'] # because we want to use it a bit later
        publications = all_publications.filter(publication__type = publication_type)
        for publication in publications:
            publication.template = "includes/" + publication_type + ".html"
            selected_publications.append(publication)
    selected_publications.sort(reverse = True, key=operator.attrgetter('publication_date'))
    #selected_publications.sort(key=lambda x: x[0].publication_date)
    return {"selected_publications": selected_publications[0:6]}


@register.inclusion_tag('all_publications.html', takes_context = True)
def get_all_person_publications(context, researcher = None):
    """   
    Lists all the Researcher's articles
    """
    if researcher == None:
        researcher = context.get('person').researcher
    all_publications = researcher.get_all_publications() \
        .distinct() \
        .order_by('-publication__type', '-publication_date')
    ordered_publications = []    
    for information in PUBLICATION_INFORMATION:
        publication_type = information['type'] # because we cant use information['type'] inside a .filter()
        publications = all_publications.filter(publication__type = publication_type).order_by('-publication_date',)
        for publication in publications:
            publication.kind = information['name']
            ordered_publications.append(publication)    
    return {
        "all_publications": ordered_publications,
      }                

@register.inclusion_tag('all_publications.html', takes_context = True)
def get_all_entity_publications(context, entity = None):
    """   
    Lists all the Entity's articles
    """
    if entity == None:
        entity = work_out_entity(context, entity)
    if entity.abstract_entity:
        real_entity = entity.get_real_ancestor()
    else: 
        real_entity = entity
    all_publications = BibliographicRecord.objects.filter(
        authored__visible = True,
        authored__researcher__person__member_of__entity__in=real_entity.get_descendants(include_self=True)) \
            .distinct() \
            .order_by('publication__type', '-publication_date')
    ordered_publications = []    
    for information in PUBLICATION_INFORMATION:
        publication_type = information['type'] # because we cant use information['type'] inside a .filter()
        publications = all_publications.filter(publication__type = publication_type).order_by('-publication_date',)
        for publication in publications:
            publication.kind = information['name']
            ordered_publications.append(publication)    
    return {
        "all_publications": ordered_publications,
        }        

@register.inclusion_tag('entity_selected_publications.html', takes_context = True)
def get_selected_entity_publications(context, heading=None, format = "short", max_items = 20, entity = None):
    """   
    Lists Entity's selected articles
    """
    selected_publications = []
    if entity == None:
        entity = work_out_entity(context, entity)
    if entity.abstract_entity:
        real_entity = entity.get_real_ancestor()
    else: 
        real_entity = entity
    all_publications = BibliographicRecord.objects.filter(authored__visible = True,
        authored__researcher__person__member_of__entity__in=real_entity.get_descendants(include_self=True)
        ).distinct()
    for information in PUBLICATION_INFORMATION:
        publication_type = information['type'] # because we want to use it a bit later
        publications = all_publications.filter(publication__type = publication_type)
        for publication in publications:
            publication.template = "includes/" + publication_type + ".html"
            selected_publications.append(publication)
    selected_publications.sort(reverse = True, key=operator.attrgetter('publication_date'))
    #selected_publications.sort(key=lambda x: x[0].publication_date)
    return {"selected_publications": selected_publications[0:max_items],
        "heading": heading,
        "format": format,
        "entity": entity,}
