"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

__all__ = ['public', 'webapp']

def init_app(app):
    from . import public, webapp
    app.register_blueprint(public.module)
    app.register_blueprint(webapp.module)

