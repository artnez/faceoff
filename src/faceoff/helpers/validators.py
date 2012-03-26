"""
Contains form validator classes designed for use with WTForms.

Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from wtforms.validators import ValidationError
from faceoff.db import use_db

class UniqueNickname(object):
    """
    Validates that a value is a unique user nickname.
    """

    def __init__(self, message=None):
        self.message = message

    @use_db
    def __call__(self, db, form, field):
        if db.find('user', nickname=field.data):
            if self.message is None:
                self.message = 'is already in use'
            raise ValidationError(self.message)
