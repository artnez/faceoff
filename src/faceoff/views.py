"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os
import logging
from flask import g, request, session, abort, redirect, url_for, send_from_directory
from faceoff import app
from faceoff.debug import debug
from faceoff.forms import LoginForm, JoinForm, ReportForm
from faceoff.helpers.decorators import authenticated, templated
from faceoff.models.user import get_active_users, create_user, auth_login, auth_logout
from faceoff.models.league import find_league, get_active_leagues
from faceoff.models.setting import get_setting

#g.active_users = get_active_users()
#g.current_league = current_league
#g.active_leagues = get_active_leagues()
#g.report_form = ReportForm(g.active_users)

@app.teardown_request
def db_close(exception): # pylint:disable=W0613
    if hasattr(g, 'db'):
        g.db.close()

@app.url_value_preprocessor
def get_league_from_url(endpoint, view_args):
    if not view_args or 'league' not in view_args:
        return
    league = find_league(slug=view_args.pop('league'))
    if league is None or league['active'] != 1:
        abort(404)
    g.current_league = league

@app.url_defaults
def add_league_to_url(endpoint, view_args):
    if ('league' not in view_args and 
        app.url_map.is_endpoint_expecting(endpoint, 'league') and 
        hasattr(g, 'current_league')):
        view_args['league'] = g.current_league['slug']

@app.context_processor
def inject_template_data():
    d = {}
    if hasattr(g, 'current_user'):
        d['current_user'] = g.current_user
    if hasattr(g, 'current_league'):
        d['current_league'] = g.current_league
    return d

@app.route('/favicon.ico')
def favicon():
    path = os.path.join(app.root_path, 'static')
    return send_from_directory(path, 'favicon.ico')

@app.route('/gate')
@templated()
def gate():
    join_form = JoinForm(access_code=get_setting('access_code'))
    return dict(login_form=LoginForm(), join_form=join_form)

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
        return redirect(url_for('dashboard'))

@app.route('/')
@authenticated
def landing():
    return 'blah'

@app.route('/<league>/')
@templated()
@authenticated
def dashboard():
    return dict(
        active_leagues = get_active_leagues(),
        report_form = ReportForm(get_active_users())
        )

@app.route('/<league>/report', methods=('POST',))
@templated()
@authenticated
def report():
    form = ReportForm(get_active_users(), request.form)
    if not form.validate():
        return dict(form=form)
    return redirect(url_for('dashboard'))

@app.route('/<league>/standings/')
@templated()
@authenticated
def standings():
    pass

@app.route('/<league>/history/')
@templated()
@authenticated
def history():
    pass
