"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import re
import string # pylint: disable=W0402
from random import choice
from time import time
from hashlib import sha1
from faceoff.db import Table

class DataModel(Table):

    def __init__(self, db):
        Table.__init__(self, db, self.get_table_name())

    def get_table_name(self):
        name = re.sub(r'Model$', '', self.__class__.__name__)
        name = re.sub(r'([A-Z])', '_\\1', name)
        return name.strip('_').lower()

class UserModel(DataModel):

    RANK_MEMBER = 'member'
    RANK_ADMIN = 'admin'

    def create(self, nickname, password, rank=None):
        salt = self.generate_salt()
        password = sha1(password + salt).hexdigest()
        rank = rank if rank in [self.RANK_MEMBER, self.RANK_ADMIN] else 'member'
        return self.insert(
            nickname = nickname, 
            password = password, 
            salt = salt,
            rank = rank,
            date_created = int(time())
            )

    def login(self, session, nickname, password):
        user = self.find(nickname=nickname)
        if user is None:
            return False
        password = sha1(password + user['salt']).hexdigest()
        if password != user['password']:
            return False
        session['user_id'] = user['id'] 
        return True

    def logout(self, session):
        session.pop('user_id')

    def generate_salt(self):
        pool = string.ascii_letters + string.digits
        return ''.join(choice(pool) for x in range(8))

class LeagueModel(DataModel):

    def create(self, name, desc=None, active=True):
        return self.insert(
            name = name,
            desc = desc,
            active = '1' if active else '0',
            date_created = int(time())
            )
