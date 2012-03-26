"""
Stores defaul application configuration settings.

Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os

# flask
LOGGER_NAME = 'faceoff'
DEBUG = os.getenv('FACEOFF_DEBUG') == '1' 
SERVER_NAME = 'faceoff.dev:5000'
SECRET_KEY = os.urandom(24)
SESSION_COOKIE_NAME = '37e52fb9896aeca927cf752c6b967a46c824c776'

# logging
LOG_LEVEL = os.getenv('FACEOFF_LOG_LEVEL')
LOG_PATH = os.getenv('FACEOFF_LOG_PATH')
LOG_FILTER = os.getenv('FACEOFF_LOG_FILTER')
LOG_IGNORE = os.getenv('FACEOFF_LOG_IGNORE')

# memcache
MEMCACHED_SERVERS = '127.0.0.1:11211'

# database
DB_PATH = os.getenv('FACEOFF_DB_PATH')
DB_FIXTURES = os.getenv('FACEOFF_DB_FIXTURES')

def init_app(app):
    app.config.from_object(__name__)
    app.config.from_envvar('FACEOFF_CONFIG', silent=True)
