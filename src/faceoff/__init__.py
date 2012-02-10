"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from flask import Flask
from faceoff import config, log, cache, db, models, modules

__all__ = ['app']

app = Flask(__name__)
config.init_app(app)
log.init_app(app)
cache.init_app(app)
db.init_app(app)
models.init_app(app)
modules.init_app(app)

