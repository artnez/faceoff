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

class CompanyModel(DataModel):
    
    def create(self, name, subdomain):
        return self.insert(
            name = name, 
            subdomain = subdomain, 
            date_created = int(time())
            )

class UserModel(DataModel):

    def create(self, company_id, nickname, password):
        salt = self.generate_salt()
        password = sha1(password + salt).hexdigest()
        return self.insert(
            company_id = company_id, 
            nickname = nickname, 
            password = password, 
            salt = salt,
            date_created = int(time())
            )

    def authenticate(self, company_id, nickname, password):
        user = self.find(company_id=company_id, nickname=nickname)
        if user is None:
            return None
        password = sha1(password + user['salt']).hexdigest()
        if password != user['password']:
            return None
        return user['id']

    def generate_salt(self):
        pool = string.ascii_letters + string.digits
        return ''.join(choice(pool) for x in range(8))

class LeagueModel(DataModel):

    def create(self, company_id, name, description=None, active=True):
        return self.insert(
            company_id = company_id,
            name = name,
            description = description,
            active = '1' if active else '0',
            date_created = int(time())
            )

