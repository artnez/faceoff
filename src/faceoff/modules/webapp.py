"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from flask import Blueprint, g, request, abort, redirect, url_for, session
from faceoff import app
from faceoff.models import CompanyModel, UserModel
from faceoff.forms import LoginForm, JoinForm
from faceoff.helpers.decorators import templated

module = Blueprint('webapp', __name__, subdomain='<company>')

@module.before_request
def before_request():
    g.db = app.db.connect()

    g.company_model = CompanyModel(g.db)
    g.company = g.company_model.find(subdomain=request.view_args.pop('company'))
    if g.company is None:
        abort(404)

    g.user_model = UserModel(g.db)
    g.user = g.user_model.find(id=session.get('user_id'))
    if g.user is None and request.endpoint[7:] not in ['gate', 'login', 'join']:
        return redirect(url_for('.gate'))

@module.url_defaults
def url_defaults(endpoint, values): # pylint: disable=W0613
    values.setdefault('company', g.company['subdomain'])

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
        user_id = g.user_model.authenticate(g.company['id'], **form.data)
        if user_id is None:
            return redirect(url_for('.login', fail=1))
        else:
            session['user_id'] = user_id
            return redirect(url_for('.home'))
    return dict(login_form=form)

@module.route('/join', methods=['GET', 'POST'])
@templated()
def join():
    form = JoinForm(request.form)
    if request.method == 'POST' and form.validate():
        # create user
        return redirect(url_for('.home'))
    return dict(join_form=form)

