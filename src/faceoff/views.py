"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os
from logging import debug
from flask import Flask, g, request, abort, redirect, url_for, session, send_from_directory
from faceoff import app
from faceoff.forms import LoginForm, JoinForm
from faceoff.helpers.decorators import templated, authenticated
from faceoff.models.league import search_leagues, find_league
from faceoff.models.user import find_user, create_user, auth_login, auth_logout
from faceoff.models.settings import get_setting

@app.teardown_request
def db_close(exception): # pylint:disable=W0613
    if hasattr(g, 'db'):
        g.db.close()

@app.url_defaults
def add_league_to_url(endpoint, view_args):
    if ('league' not in view_args and 
        app.url_map.is_endpoint_expecting(endpoint, 'league') and 
        'league' in request.view_args):
        league = request.view_args['league']
        view_args['league'] = league['slug'] if 'slug' in league else league

@app.url_value_preprocessor
def get_league_from_url(endpoint, view_args):
    if not view_args or 'league' not in view_args:
        return
    slug = view_args['league'].split('-')[0]
    league = find_league(slug=slug)
    if league is None:
        abort(404)
    view_args['league'] = league

@app.route('/favicon.ico')
def favicon():
    path = os.path.join(app.root_path, 'static')
    return send_from_directory(path, 'favicon.ico')

@app.route('/')
@authenticated
def landing():
    return 'blah'

@app.route('/<league>/')
@templated()
@authenticated
def dashboard(league):
    pass

@app.route('/<league>/stats/')
@templated()
@authenticated
def stats(league):
    pass

@app.route('/<league>/history/')
@templated()
@authenticated
def history(league):
    pass

@app.route('/gate')
@templated()
def gate():
    return dict(login_form=LoginForm(), 
                join_form=JoinForm(access_code=get_setting('access_code')))

@app.route('/login', methods=['GET', 'POST'])
@templated()
def login():
    form = LoginForm(request.form)
    if request.method != 'POST' or not form.validate():
        return dict(login_form=form)
    if auth_login(session, **form.data):
        return redirect(url_for('landing'))
    else:
        return redirect(url_for('login', fail=1))

@app.route('/logout')
def logout():
    auth_logout(session)
    return redirect(url_for('gate'))

@app.route('/join', methods=['GET', 'POST'])
@templated()
def join():
    form = JoinForm(request.form, access_code=get_setting('access_code'))
    if request.method != 'POST' or not form.validate():
        return dict(join_form=form)
    else:
        user_id = create_user(form.nickname.data, form.password.data)
        session['user_id'] = user_id
        return redirect(url_for('landing'))
