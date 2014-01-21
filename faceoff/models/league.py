"""
Copyright: (c) 2012-2014 Artem Nezvigin <artem@artnez.com>
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
def get_inactive_leagues(db):
    return search_leagues(db, active=0)


@use_db
def create_league(db, name, description=None, active=True):
    name = name.strip()
    return db.insert(
        'league',
        name=name,
        slug=generate_league_slug(db, name),
        description=description,
        active='1' if active else '0',
        date_created=int(time()))


@use_db
def update_league(db, league_id, name=None, active=None):
    league = find_league(db, id=league_id)
    if league is None:
        return False
    fields = {}
    if name is not None:
        name = name.strip()
        slug = league['slug'] if name == league['name'] else \
            generate_league_slug(db, name)
        fields['name'] = name
        fields['slug'] = slug
    if active is not None:
        fields['active'] = '1' if active else '0'
    db.update('league', league_id, **fields)
    return find_league(db, id=league_id)


@use_db
def generate_league_slug(db, name):
    short = re.sub(r'[^0-9a-zA-Z]+', '-', name.lower()).strip('-')
    count = 0
    while True:
        slug = short + str(count) if count > 0 else short
        if find_league(db, slug=slug) is None:
            break
        count += 1
    return slug
