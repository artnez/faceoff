"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os
import re
import string
import json
from random import choice, shuffle, randint
from time import time
from hashlib import sha1
from logging import getLogger
from jinja2.utils import generate_lorem_ipsum
from faceoff.db import Table

_curdir = os.path.dirname(__file__)
_fixtures = os.path.join(_curdir, 'schema', 'fixtures.json')
_logger = None

def init_app(app):
    if app.debug and not os.getenv('WERKZEUG_RUN_MAIN'):
        fixtures = FixturesModel(app.db.connect())
        fixtures.build_all()

def logger():
    global _logger
    if _logger is None:
        _logger = getLogger('model')
    return _logger

class DataModel(Table):

    def __init__(self, db):
        Table.__init__(self, db, self.get_table_name())

    def get_table_name(self):
        name = re.sub(r'Model$', '', self.__class__.__name__)
        name = re.sub(r'([A-Z])', '_\\1', name)
        return name.strip('_').lower()

class CompanyModel(DataModel):
    
    def create(self, name, subdomain):
        return self.insert(
            name = name, 
            subdomain = subdomain, 
            date_created = int(time())
            )

class UserModel(DataModel):

    def create(self, company_id, nickname, email, password):
        salt = self.generate_salt()
        password = sha1(password + salt).hexdigest()
        return self.insert(
            company_id = company_id, 
            nickname = nickname, 
            email = email, 
            password = password, 
            salt = salt,
            date_created = int(time())
            )

    def generate_salt(self):
        pool = string.ascii_letters + string.digits
        return ''.join(choice(pool) for x in range(8))

class LeagueModel(DataModel):

    def create(self, company_id, name, info=None, active=True):
        return self.insert(
            company_id = company_id,
            name = name,
            info = info,
            active = '1' if active else '0',
            date_created = int(time())
            )

class FixturesModel:

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

    def build_companies(self, min=3, max=6):
        logger().info('building fixtures: companies')
        for company in self.pick_companies(min, max):
            self.company.create(**company)

    def build_users(self, min=3, max=10):
        logger().info('building fixtures: users')
        for company in self.company.search():
            for user in self.pick_users(min, max):
                self.user.create(company_id=company['id'], **user)

    def build_leagues(self, min=1, max=5):
        logger().info('building fixtures: leagues')
        for company in self.company.search():
            for league in self.pick_leagues(min, max):
                self.league.create(company_id=company['id'], **league)

    def pick_users(self, min, max):
        for person in self.pick_data('people', min, max):
            fname, lname = person['fname'].lower(), person['lname'].lower()
            nick = fname[0] + lname
            email = '%s.%s@example.com' % (fname, lname)
            yield {'nickname': nick, 'email': email, 'password': 'p!ngp0ng!'}

    def pick_companies(self, min, max):
        for company in self.pick_data('companies', min, max):
            yield company

    def pick_leagues(self, min, max):
        for game in self.pick_data('games', min, max):
            name = game['name']
            info = self.pick_text(1, 3)
            active = True if randint(0, 3) else False
            yield {'name': name, 'info': info, 'active': active}

    def pick_text(self, min, max):
        return generate_lorem_ipsum(n=randint(min, max), html=False)

    def pick_data(self, source, min, max):
        return [self.data[source][n] for n in range(randint(min, max))]

    def load_data(self):
        with open(os.path.join(_fixtures)) as f:
            fixtures = json.loads(f.read())
        for category in fixtures:
            shuffle(fixtures[category])
        return fixtures

    def truncate(self):
        models = ['company', 'user', 'league']
        [getattr(self, model).truncate() for model in models]

