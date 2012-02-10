"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from flask import Blueprint, g, request, abort, redirect, url_for
from faceoff import app
from faceoff.forms import LoginForm, JoinForm
from faceoff.helpers.decorators import templated

module = Blueprint('webapp', __name__, subdomain='<company>', static_folder='../static')

@module.before_request
def before_request():
    g.company = request.view_args.pop('company')
    g.user = None

@module.url_defaults
def url_defaults(endpoint, values):
    values.setdefault('company', g.company)

@module.route('/')
@templated()
def home():
    pass

@module.route('/gate')
@templated()
def gate():
    return dict(login_form=LoginForm(), join_form=JoinForm())

@module.route('/login', methods=['GET', 'POST'])
@templated()
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('dashboard'))
    return dict(login_form=form)

@module.route('/join', methods=['GET', 'POST'])
@templated()
def join():
    form = JoinForm(request.form)
    if request.method == 'POST' and form.validate():
        # create user
        return redirect(url_for('dashboard'))
    return dict(join_form=form)

