"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from wtforms import Form, TextField, SelectField, RadioField
from wtforms.widgets import PasswordInput
from wtforms.validators import Required, Length, Regexp, EqualTo, AnyOf
from faceoff.helpers.validators import UniqueNickname
from faceoff.db import get_connection

class PasswordField(TextField):
    widget = PasswordInput(hide_value=False)

class ReportForm(Form):
    opponent = SelectField('Who did you play?', choices=[])
    result = RadioField('Did you win?', choices=[('1', 'Yes'), ('0', 'No')])

class LoginForm(Form):
    nickname = TextField('Nickname', [Required()])
    password = PasswordField('Password', [Required()])

class JoinForm(Form):
    nickname = TextField(
        label='Nickname', 
        id='join_nickname', 
        validators=[Required(), Length(2, 20), Regexp(r'^[a-zA-Z0-9_]+$'), UniqueNickname()]
        )
    password = PasswordField(
        label='Password', 
        id='join_password',
        validators=[Required(), Length(4), EqualTo('confirm')]
        )
    confirm = PasswordField(
        label='Repeat Password',
        id='join_confirm'
        )
    access_code = PasswordField(
        label='Access Code', 
        id='join_access_code',
        validators=[Required()],
        description='Someone should have given you the code.'
        )

    def __init__(self, *args, **kwargs):
        """
        Allow passing an 'access_code' keyword arg. Without this arg, the access
        code field is removed. With the access_code, an additional validator is 
        created that includes the code.
        """
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
