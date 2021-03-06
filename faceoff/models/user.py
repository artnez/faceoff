"""
Copyright: (c) 2012-2014 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import string
from random import choice
from time import time
from hashlib import sha1
from faceoff.db import use_db, Expr

RANK_ADMIN = 'admin'
RANK_MEMBER = 'member'


@use_db
def find_user(db, **kwargs):
    return db.find('user', **kwargs)


@use_db
def find_user_id(db, nickname):
    user = db.find('user', nickname=nickname)
    return None if user is None else user['id']


@use_db
def search_users(db, **kwargs):
    return db.search('user', **kwargs)


@use_db
def get_all_users(db):
    return search_users(db)


@use_db
def get_active_users(db):
    return search_users(db, sort=Expr('UPPER(nickname)'), order='asc')


@use_db
def create_user(db, nickname, password, rank=None):
    """
    Creates a new faceoff user. Returns the newly created user ID on success.
    """
    salt = generate_salt()
    password = sha1(password + salt).hexdigest()
    rank = rank if rank in [RANK_MEMBER, RANK_ADMIN] else RANK_MEMBER
    return db.insert(
        'user',
        nickname=nickname,
        password=password,
        salt=salt,
        rank=rank,
        date_created=int(time()))


@use_db
def update_user(db, user_id, nickname=None, password=None):
    user = find_user(db, id=user_id)
    if user is None:
        return False
    fields = {}
    if nickname is not None and nickname != user['nickname']:
        fields['nickname'] = nickname
    if password is not None and password != '':
        fields['salt'] = generate_salt()
        fields['password'] = sha1(password + fields['salt']).hexdigest()
    db.update('user', user_id, **fields)
    return find_user(db, id=user_id)


@use_db
def auth_login(db, session, nickname, password):
    """
    Attempts to the authenticate a faceoff user with the given nickname and
    password. If successful, the provided session object is changed to an
    authenticated state.

    NOTE: If the application grows, this will likely need to be moved into a
    model that is exclusively responsible for auth management.
    """
    user = db.find('user', nickname=nickname)
    if user is None:
        return False
    password = sha1(password + user['salt']).hexdigest()
    if password != user['password']:
        return False
    session['user_id'] = user['id']
    session.permanent = True
    return True


def auth_logout(session):
    """
    Removes an authenticated state from the given session.

    NOTE: If the application grows, this will likely need to be moved into a
    model that is exclusively responsible for auth management.
    """
    if 'user_id' in session:
        session.pop('user_id')


def generate_salt():
    """
    Generates a random user salt that will protect against hash table attacks
    should the database be compromised.
    """
    pool = string.ascii_letters + string.digits
    return ''.join(choice(pool) for x in range(8))
