"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

def attach_jinja(jinja_env):
    """
    Attaches all filters in this module to the given Jinja environment.
    """
    jinja_env.filters['dump'] = dump

def dump(obj):
    """
    Returns a representation of the given object's attributes.
    """
    return repr(vars(obj))
