from django import template

from publications.models import BibliographicRecord
from publications.lister import (
    PublicationsLister, PublicationsListForPerson,
    PublicationsArchiveListForPerson
    )

register = template.Library()


@register.inclusion_tag(
    'arkestra/generic_lister.html',
    takes_context = True
    )
def get_selected_person_publications(context, researcher = None):
    """
    Lists Researcher's selected articles
    """
    researcher = researcher or context.get('person').researcher
    # invoke the lister to find out more
    lister = PublicationsLister(
        listkinds=[
            ("publications", PublicationsListForPerson),
                ],
        researcher=researcher,
        heading_text="Recent key publications",
        limit_to=6,
        favourites_only=True,
        request=context["request"],
        )
    context.update({"lister": lister})
    return context


@register.inclusion_tag(
    'arkestra/generic_filter_list.html',
    takes_context = True
    )
def get_all_person_publications(context, researcher = None):
    researcher = researcher or context.get('person').researcher
    # invoke the lister to find out more
    lister = PublicationsLister(
        listkinds=[
            ("publications", PublicationsArchiveListForPerson),
                ],
        researcher=researcher,
        request=context["request"],
        )
    context.update({"lister": lister})
    return context
