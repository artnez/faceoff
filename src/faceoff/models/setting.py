"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from faceoff.db import use_db

@use_db
def get_setting(db, name, default=None):
    setting = db.find('setting', name=name)
    if setting is None:
        return default
    return setting['value']

@use_db
def set_setting(db, name, value=None):
    setting = db.find('setting', name=name)
    if setting is None:
        query = 'INSERT INTO setting (name, value) VALUES (?, ?)'
    else:
        query = 'UPDATE setting SET value=? WHERE name=?'
    db.execute(query, (name, value))
