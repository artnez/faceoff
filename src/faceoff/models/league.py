"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import re
from time import time
from faceoff.db import use_db

@use_db
def find_league(db, **kwargs):
    return db.find('league', **kwargs)

@use_db
def search_leagues(db, **kwargs):
    return db.search('league', **kwargs)

@use_db
def get_all_leagues(db):
    return search_leagues(db)

@use_db
def get_active_leagues(db):
    return search_leagues(db, active=1)

@use_db
def create_league(db, name, description=None, active=True):
    name = name.strip()
    return db.insert(
        'league',
        name = name,
        slug = generate_league_slug(db, name),
        description = description,
        active = '1' if active else '0',
        date_created = int(time())
        )

@use_db
def change_league_name(db, league_id, name, slug=None):
    league = find_league(db, id=league_id)
    name = name.strip()
    if league is None or league['name'] == name:
        return league
    db.update(
        'league', 
        league_id, 
        name = name, 
        slug = generate_league_slug(db, name)
        )
    return find_league(db, id=league_id)

@use_db
def generate_league_slug(db, name, omit=None):
    short = re.sub(r'[^0-9a-zA-Z]+', '-', name.lower()).strip('-')
    count = 0
    while True:
        slug = short + str(count) if count > 0 else short
        if find_league(db, slug=slug) is None:
            break
        count += 1
    return slug
