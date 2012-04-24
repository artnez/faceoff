"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import logging
from flask import Flask, g, request, abort, redirect, url_for, session
from faceoff import app
from faceoff.forms import LoginForm, JoinForm
from faceoff.helpers.decorators import templated, authenticated
from faceoff.models.league import search_leagues
from faceoff.models.user import find_user, create_user, auth_login, auth_logout
from faceoff.models.settings import get_setting

@app.teardown_request
def db_close(exception): # pylint:disable=W0613
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
@authenticated
def landing():
    return 'blah'

@app.route('/<league>/')
@templated()
@authenticated
def dashboard(league):
    leagues = search_leagues()
    return dict(leagues=leagues)

@app.route('/stats')
@templated()
@authenticated
def stats():
    pass

@app.route('/history')
@templated()
@authenticated
def history():
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
