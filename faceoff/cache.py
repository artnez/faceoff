"""
Copyright: (c) 2012-2014 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from werkzeug.contrib.cache import NullCache, MemcachedCache


def init_app(app):
    """
    Configures the provided app cache services.
    """
    servers = app.config['MEMCACHED_SERVERS']
    servers = filter(None, servers.split(',') if servers is str else servers)
    app.cache = MemcachedCache(servers) if servers else NullCache()
