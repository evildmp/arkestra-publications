from .models import BibliographicRecord, publication_kinds
from links import schema


def url(obj):
    return obj.get_url() or "No URL available"


def metadata(obj):
    kind = publication_kinds[obj.publication.type]

    if obj.publication.type == "journal-article":
        return "%s in %s, %s" % (kind, obj.journal, obj.get_publication_date())

    return publication_kinds[obj.publication.type]

schema.register(
    BibliographicRecord,
    search_fields=["title", "authors"],
    heading='"Publications"',
    url=url,
    admin_metadata=metadata,
    summary="authors"
    )
