"""
Populates the database with sample data for testing.

Copyright: (c) 2012-2014 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os
from logging import getLogger
from time import mktime
from datetime import datetime, timedelta
from random import shuffle, randint
from jinja2.utils import generate_lorem_ipsum
from faceoff.models.user import create_user, get_active_users
from faceoff.models.league import (
    create_league, get_all_leagues, get_active_leagues)
from faceoff.models.match import create_match, rebuild_rankings
from faceoff.models.setting import set_setting

_logger = None

HUMAN_NAMES = [
    ['Wayne', 'Gretzky'], ['Bobby', 'Orr'], ['Gordie', 'Howe'],
    ['Mario', 'Lemieux'], ['Maurice', 'Richard'], ['Doug', 'Harvey'],
    ['Jean', 'Beliveau'], ['Bobby', 'Hull'], ['Terry', 'Sawchuk'],
    ['Eddie', 'Shore'], ['Guy', 'Lafleur'], ['Mark', 'Messier'],
    ['Jacques', 'Plante'], ['Ray', 'Bourque'], ['Howie', 'Morenz'],
    ['Glenn', 'Hall'], ['Stan', 'Mikita'], ['Phil', 'Esposito'],
    ['Denis', 'Potvin'], ['Mike', 'Bossy'], ['Ted', 'Lindsay'],
    ['Patrick', 'Roy'], ['Red', 'Kelly'], ['Bobby', 'Clarke'],
    ['Larry', 'Robinson'], ['Ken', 'Dryden'], ['Frank', 'Mahovlich'],
    ['Milt', 'Schmidt'], ['Paul', 'Coffey'], ['Henri', 'Richard'],
    ['Bryan', 'Trottier'], ['Dickie', 'Moore'], ['Newsy', 'Lalonde'],
    ['Syl', 'Apps'], ['Bill', 'Durnan'], ['Charlie', 'Conacher'],
    ['Jaromir', 'Jagr'], ['Marcel', 'Dionne'], ['Joe', 'Malone'],
    ['Chris', 'Chelios'], ['Dit', 'Clapper'], ['Bernie', 'Geoffrion'],
    ['Tim', 'Horton'], ['Bill', 'Cook'], ['Johnny', 'Bucyk'],
    ['George', 'Hainsworth'], ['Gilbert', 'Perreault'], ['Max', 'Bentley'],
    ['Brad', 'Park'], ['Jari', 'Kurri']]

GAME_NAMES = [
    'Table Tennis', 'Chess', 'Thumb Wrestling', 'Foosball', 'Boxing',
    'Checkers', 'Scrabble', 'Poker', 'Billiards', 'Basketball',
    'Flag Football', 'Horseshoes', 'Backgammon', 'Shuffleboard', 'Archery',
    'Air Hockey', 'Bowling', 'Tetris', 'Street Fighter']

COMPANY_NAMES = [
    ["Aperture Science"], ["BiffCo Enterprises"], ["Bluth Company"],
    ["Dunder Mifflin"], ["Globo Gym"], ["InGen"], ["Kramerica"],
    ["Oceanic Airlines"], ["Omni Consumer Products"], ["Oscorp Industries"],
    ["Rekall Incorporated"], ["Sterling Cooper Draper Pryce"],
    ["Tyrell Corporation"], ["Umbrella Corporation"]]


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
    db.execute('begin exclusive')
    db.is_building = True
    generate_settings(db)
    generate_users(db, truncate=truncate)
    generate_leagues(db, truncate=truncate)
    generate_matches(db, truncate=truncate)
    db.commit()
    logger().info('rebuilding rankings...')
    [rebuild_rankings(db, league['id']) for league in get_all_leagues(db)]
    db.is_building = False


def generate_users(db, min_count=4, max_count=12, truncate=False):
    """
    Generates a random amount of users into the given database connection
    object. The amount of users will fall between `min_count` and `max_count`.
    If `truncate` is True, all existing users will be deleted.
    """
    logger().info('creating users')
    if truncate:
        db.truncate_table('user')
    users = []
    for user in rand_users(min_count=min_count, max_count=max_count):
        users.append(create_user(db=db, **user))
    logger().info('created %d users' % len(users))
    return users


def generate_leagues(db, min_count=2, max_count=6, truncate=False):
    """
    Generates a random amount of leagues into the given database connection
    object. The amount of leagues will fall between `min_count` and
    `max_count`. If `truncate` is True, all existing leagues will be deleted.
    """
    logger().info('creating leagues')
    if truncate:
        db.truncate_table('league')
    leagues = []
    for league in rand_leagues(min_count, max_count):
        league_id = create_league(db=db, **league)
        leagues.append(league_id)
    logger().info('created %d leagues' % len(leagues))
    return leagues


def generate_settings(db):
    """
    Generates default application settings.
    """
    set_setting('access_code', 'letmeplay', db=db)


def generate_matches(db, truncate=False):
    """
    Generates new matches between players in a league.
    """
    if truncate:
        db.truncate_table('match')
    users = get_active_users(db)
    leagues = get_active_leagues(db)
    for league in leagues:
        logger().info('creating matches for league: %s' % league['name'])
        matches = []
        for i in range(randint(0, 25)):
            shuffle(users)
            winner = users[0]['id']
            loser = users[1]['id']
            matches.append([league, winner, loser])
        match_date = datetime.now() - timedelta(days=100)
        diff_hours = round(100.0/len(matches), 2)
        for match in matches:
            match_date = match_date + timedelta(hours=diff_hours*24)
            match_time = mktime(match_date.timetuple())
            create_match(
                db, match[0]['id'], match[1], match[2], match_date=match_time)


def rand_users(min_count, max_count):
    """
    Returns a list of random objects that map the properties of a user record.
    """
    names = HUMAN_NAMES
    shuffle(names)
    count = randint(min_count, max_count)
    names.insert(0, ['a', 'rtnez'])
    for n in range(count):
        fname = names[n][0].lower() if randint(0, 1) else names[n][0]
        lname = names[n][1].lower() if randint(0, 1) else names[n][1]
        nickname = fname + lname
        rank = 'admin' if n < 2 else 'member'
        yield {'nickname': nickname, 'password': 'faceoff!', 'rank': rank}


def rand_leagues(min_count, max_count):
    """
    Returns a list of random objects that map the properties of a league
    record.
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
