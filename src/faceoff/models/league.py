"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from time import time
from faceoff.db import use_db

@use_db
def search_leagues(db, **kwargs):
    return db.search('league', **kwargs)

@use_db
def create_league(db, name, description=None, active=True):
    return db.insert(
        'league',
        name = name,
        description = description,
        active = '1' if active else '0',
        date_created = int(time())
        )

@use_db
def add_league_member(db, league_id, user_id):
    return db.insert(
        'league_member',
        user_id=user_id,
        league_id=league_id
        )
