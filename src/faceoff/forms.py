"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from wtforms import Form, TextField
from wtforms.widgets import PasswordInput
from wtforms.validators import Required, Length, Regexp, EqualTo, AnyOf
from faceoff.helpers.validators import UniqueNickname
from faceoff.db import get_connection

class PasswordField(TextField):
    widget = PasswordInput(hide_value=False)

class LoginForm(Form):
    nickname = TextField('Nickname', [Required()])
    password = PasswordField('Password', [Required()])

class JoinForm(Form):
    nickname = TextField('Nickname', [
        Required(), 
        Length(2, 20), 
        Regexp(r'^[a-zA-Z0-9_]+$', message='only numbers, letters, and underscores allowed.'),
        UniqueNickname()
        ])
    password = PasswordField('Password', [
        Required(), 
        Length(4, message='must be at least 4 characters'), 
        EqualTo('confirm', message='passwords must match')
        ])
    confirm = PasswordField('Repeat Password')
    access_code = PasswordField('Access Code', [Required()],
        description='Someone should have given you the code.'
        )

    def __init__(self, *args, **kwargs):
        access_code = None
        if kwargs.has_key('access_code'):
            access_code = kwargs['access_code'] 
            del kwargs['access_code']
        super(JoinForm, self).__init__(*args, **kwargs)
        if access_code is None:
            del self.access_code
        else:
            validator = AnyOf([access_code], message='that code is wrong')
            self.access_code.validators.append(validator)
