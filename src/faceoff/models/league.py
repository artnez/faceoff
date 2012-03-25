"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from time import time
from faceoff.db import use_db

@use_db
def create_league(db, name, desc=None, active=True):
    """
    Creates a new faceoff league. Returns the new league's ID on success.
    """
    return db.insert(
        'league',
        name = name,
        desc = desc,
        active = '1' if active else '0',
        date_created = int(time())
        )
