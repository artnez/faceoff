"""
Stores default application configuration settings.

Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os

# flask
LOGGER_NAME = 'faceoff'
DEBUG = os.getenv('FACEOFF_DEBUG') == '1' 
SERVER_NAME = 'faceoff.dev:5000'
SECRET_KEY = '89a1100b5a62059021260a75738e6e61' if DEBUG else os.urandom(24)

# logging
LOG_LEVEL = os.getenv('FACEOFF_LOG_LEVEL')
LOG_PATH = os.getenv('FACEOFF_LOG_PATH')
LOG_FILTER = os.getenv('FACEOFF_LOG_FILTER')
LOG_IGNORE = os.getenv('FACEOFF_LOG_IGNORE')

# memcache
MEMCACHED_SERVERS = 'localhost:1121'

# database
DB_PATH = os.getenv('FACEOFF_DB_PATH')
DB_FIXTURES = os.getenv('FACEOFF_DB_FIXTURES')

def init_app(app):
    app.config.from_object(__name__)
    app.config.from_envvar('FACEOFF_CONFIG', silent=True)
    app.config.from_pyfile('/etc/faceoff.py', silent=True)
