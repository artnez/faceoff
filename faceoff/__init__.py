"""
Copyright: (c) 2012-2014 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from flask import Flask
from faceoff import config, log, cache, db, fixtures, tpl

__all__ = ['app']

app = Flask(__name__)
config.init_app(app)
log.init_app(app)
cache.init_app(app)
db.init_app(app)
fixtures.init_app(app)
tpl.init_app(app)

import faceoff.views  # flake8: noqa
