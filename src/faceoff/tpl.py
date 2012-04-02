"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from helpers import filters

def init_app(app):
    """
    Configures the provided app with template helpers. Expects an object, but 
    will be made more sophisticated as needed. This is for debugging uses.
    """
    filters.attach_jinja(app.jinja_env)
