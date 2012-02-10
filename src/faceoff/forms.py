"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from wtforms import Form, TextField, PasswordField
from wtforms.validators import Required, Email, EqualTo

class LoginForm(Form):
    email = TextField('Email Address', [Required(), Email()])
    password = PasswordField('Password', [Required()])

class JoinForm(Form):
    nickname = TextField('Nickname', [Required(), Email()])
    email = TextField('Email Address', [Required(), Email()])
    password = PasswordField('Password', [Required(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

