"""
Populates the database with sample data for testing.

Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os
from logging import getLogger
from random import choice, shuffle, randint
from jinja2.utils import generate_lorem_ipsum
import json
from faceoff.models import CompanyModel, UserModel, LeagueModel

_curdir = os.path.dirname(__file__)
_fixtures = os.path.join(_curdir, 'schema', 'fixtures.json')
_logger = None

def init_app(app):
    if app.debug and not os.getenv('WERKZEUG_RUN_MAIN'):
        builder = Builder(app.db.connect())
        builder.build_all()

def logger():
    global _logger
    if _logger is None:
        _logger = getLogger('fixtures')
    return _logger

class Builder(object):

    def __init__(self, db):
        self.db = db
        self.company = CompanyModel(db)
        self.user = UserModel(db)
        self.league = LeagueModel(db)
        self.data = self.load_data()

    def build_all(self):
        logger().info('building fixtures: all')
        self.db.execute('begin')
        self.truncate()
        self.build_companies()
        self.build_users()
        self.build_leagues()
        self.db.commit()

    def build_companies(self, minCount=3, maxCount=6):
        logger().info('building fixtures: companies')
        self.company.create(
            name='Artnez',
            subdomain='artnez'
            )
        for company in self.pick_companies(minCount, maxCount):
            self.company.create(**company)

    def build_users(self, minCount=3, maxCount=10):
        logger().info('building fixtures: users')
        for company in self.company.search():
            self.user.create(
                company_id=company['id'],
                nickname='artnez',
                email='artem@artnez.com',
                password='p!ngp0ng!'
                )
            for user in self.pick_users(minCount, maxCount):
                self.user.create(company_id=company['id'], **user)

    def build_leagues(self, minCount=1, maxCount=5):
        logger().info('building fixtures: leagues')
        for company in self.company.search():
            for league in self.pick_leagues(minCount, maxCount):
                self.league.create(company_id=company['id'], **league)

    def pick_users(self, minCount, maxCount):
        for person in self.pick_data('people', minCount, maxCount):
            fname, lname = person['fname'].lower(), person['lname'].lower()
            nick = fname[0] + lname
            email = '%s.%s@example.com' % (fname, lname)
            yield {'nickname': nick, 'email': email, 'password': 'p!ngp0ng!'}

    def pick_companies(self, minCount, maxCount):
        for company in self.pick_data('companies', minCount, maxCount):
            yield company

    def pick_leagues(self, minCount, maxCount):
        for game in self.pick_data('games', minCount, maxCount):
            name = game['name']
            info = self.pick_text(1, 3)
            active = True if randint(0, 3) else False
            yield {'name': name, 'info': info, 'active': active}

    def pick_text(self, minCount, maxCount):
        return generate_lorem_ipsum(n=randint(minCount, maxCount), html=False)

    def pick_data(self, source, minCount, maxCount):
        return [self.data[source][n] for n in range(randint(minCount, maxCount))]

    def load_data(self):
        with open(os.path.join(_fixtures)) as f:
            fixtures = json.loads(f.read())
        for category in fixtures:
            shuffle(fixtures[category])
        return fixtures

    def truncate(self):
        models = ['company', 'user', 'league']
        [getattr(self, model).truncate() for model in models]

