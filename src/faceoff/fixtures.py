"""
Populates the database with sample data for testing.

Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os
from logging import getLogger, debug
from random import choice, shuffle, randint
from jinja2.utils import generate_lorem_ipsum
import json
from faceoff.models.user import create_user, all_users
from faceoff.models.league import create_league, add_league_member
from faceoff.models.setting import set_setting

_logger = None

HUMAN_NAMES = [
    ['Wayne','Gretzky'], ['Bobby','Orr'], ['Gordie','Howe'], 
    ['Mario','Lemieux'],['Maurice','Richard'], ['Doug','Harvey'], 
    ['Jean','Beliveau'],['Bobby','Hull'], ['Terry','Sawchuk'], 
    ['Eddie','Shore'], ['Guy','Lafleur'], ['Mark','Messier'], 
    ['Jacques','Plante'], ['Ray','Bourque'],['Howie','Morenz'], 
    ['Glenn','Hall'], ['Stan','Mikita'], ['Phil','Esposito'],['Denis','Potvin'], 
    ['Mike','Bossy'], ['Ted','Lindsay'], ['Patrick','Roy'],['Red','Kelly'], 
    ['Bobby','Clarke'], ['Larry','Robinson'], ['Ken','Dryden'],
    ['Frank','Mahovlich'], ['Milt','Schmidt'], ['Paul','Coffey'],
    ['Henri','Richard'], ['Bryan','Trottier'], ['Dickie','Moore'],
    ['Newsy','Lalonde'], ['Syl','Apps'], ['Bill','Durnan'], 
    ['Charlie','Conacher'],['Jaromir','Jagr'], ['Marcel','Dionne'], 
    ['Joe','Malone'], ['Chris','Chelios'],['Dit','Clapper'], 
    ['Bernie','Geoffrion'], ['Tim','Horton'], ['Bill','Cook'],
    ['Johnny','Bucyk'], ['George','Hainsworth'], ['Gilbert','Perreault'],
    ['Max','Bentley'], ['Brad','Park'], ['Jari','Kurri']
    ]

GAME_NAMES = [
    'Table Tennis', 'Chess', 'Thumb Wrestling', 'Foosball', 'Boxing', 
    'Checkers', 'Scrabble', 'Poker'
    ]

COMPANY_NAMES = [
    ["Aperture Science"], ["BiffCo Enterprises"],["Bluth Company"],
    ["Dunder Mifflin"], ["Globo Gym"],["InGen"],["Kramerica"],
    ["Oceanic Airlines"], ["Omni Consumer Products"],["Oscorp Industries"],
    ["Rekall Incorporated"], ["Sterling Cooper Draper Pryce"],
    ["Tyrell Corporation"], ["Umbrella Corporation"]
    ]

def init_app(app):
    """
    Generates fixtures configured from the state of an app object.
    """
    if app.config['DB_FIXTURES'] and not os.getenv('WERKZEUG_RUN_MAIN'):
        generate_full_db(app.db.connect(), truncate=True)

def generate_full_db(db, truncate=False):
    """
    Generates a complete database of data. Requires a valid database connection 
    object. If truncate is set to True, all existing data will be removed.
    """
    logger().info('generating full db')
    db.execute('begin')
    generate_users(db, truncate=truncate)
    generate_leagues(db, truncate=truncate)
    generate_settings(db)
    db.commit()

def generate_users(db, min_count=5, max_count=20, truncate=False):
    """
    Generates a random amount of users into the given database connection
    object. The amount of users will fall between `min_count` and `max_count`. 
    If `truncate` is True, all existing users will be deleted.
    """
    logger().info('creating users')
    if truncate:
        db.truncate_table('user')
    users = []
    for user in rand_users(min_count, max_count):
        users.append(create_user(db=db, **user))
    logger().info('created %d users (%s)' % (len(users), ','.join(users)))
    return users

def generate_leagues(db, min_count=2, max_count=5, truncate=False):
    """
    Generates a random amount of leagues into the given database connection
    object. The amount of leagues will fall between `min_count` and `max_count`. 
    If `truncate` is True, all existing leagues will be deleted.
    """
    logger().info('creating leagues')
    if truncate:
        db.truncate_table('league')
    leagues = []
    users = all_users(db=db)
    for league in rand_leagues(min_count, max_count):
        league_id = create_league(db=db, **league)
        leagues.append(league_id)
        for user in users:
            if randint(0, 2) == 2:
                add_league_member(league_id, user['id'], db=db)
    logger().info('created %d leagues (%s)' % (len(leagues), ','.join(leagues)))
    return leagues

def generate_settings(db):
    """
    Generates default application settings.
    """
    set_setting('access_code', 'letmeplay', db=db)

def rand_users(min_count=3, max_count=10):
    """
    Returns a list of random objects that map the properties of a user record.
    """
    names = HUMAN_NAMES
    shuffle(names)
    count = randint(min_count, max_count)
    names.insert(0, ['a', 'rtnez'])
    for n in range(count):
        nickname = names[n][0].lower() + names[n][1].lower()
        rank = 'admin' if n < 2 else 'member'
        yield {'nickname': nickname, 'password': 'faceoff!', 'rank': rank}

def rand_leagues(min_count=2, max_count=5):
    """
    Returns a list of random objects that map the properties of a league record.
    """
    games = GAME_NAMES
    shuffle(games)
    count = randint(min_count, max_count)
    for n in range(count):
        name = games[n]
        desc = rand_text(1, 3)
        active = True if randint(0, 3) else False
        yield {'name': name, 'description': desc, 'active': active}

def rand_text(min_count, max_count):
    """
    Returns randomly generated text with the given paragraph count.
    """
    return generate_lorem_ipsum(n=randint(min_count, max_count), html=False)

def logger():
    """
    Returns a global logger object used for debugging.
    """
    global _logger
    if _logger is None:
        _logger = getLogger('fixtures')
    return _logger
