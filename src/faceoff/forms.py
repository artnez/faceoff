"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from wtforms import Form, TextField, PasswordField
from wtforms.validators import Required, Length, Regexp, EqualTo

class LoginForm(Form):
    nickname = TextField('Nickname', [Required()])
    password = PasswordField('Password', [Required()])

class JoinForm(Form):
    nickname = TextField('Nickname', [
        Required(), 
        Length(2, 20), 
        Regexp(r'^[a-zA-Z0-9_]+$', message='Only numbers, letters, and underscores allowed.')
        ])
    password = PasswordField('Password', [
        Required(), 
        Length(4, message='Must be at least 4 characters'), 
        EqualTo('confirm', message='Passwords must match')
        ])
    confirm = PasswordField('Repeat Password')
    access_code = TextField('Access Code', description='Someone should have given you the code. If not, try buying them a beer.')
