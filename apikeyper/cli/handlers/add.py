from .core import register
from apikeyper.database import APIKeyDB


@register('add')
def do_add(ns):
    """Add an API key to the database."""
    APIKeyDB.add(ns.apikey,)


