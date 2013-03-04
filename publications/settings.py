from django.conf import settings

PUBLICATIONS_CACHE_DURATION = getattr(settings, "PUBLICATIONS_CACHE_DURATION", 60 * 60 * 6)
