"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from wtforms import Form, TextField, PasswordField
from wtforms.validators import Required, EqualTo

class LoginForm(Form):
    nickname = TextField('Nickname', [Required()])
    password = PasswordField('Password', [Required()])

class JoinForm(Form):
    nickname = TextField('Nickname', [Required()])
    password = PasswordField('Password', [Required(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

