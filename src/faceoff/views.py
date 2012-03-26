"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from flask import Flask, g, request, abort, redirect, url_for, session
from faceoff import app
from faceoff.forms import LoginForm, JoinForm
from faceoff.helpers.decorators import templated, authenticated
from faceoff.models.user import find_user, create_user, auth_login, auth_logout

@app.teardown_request
def db_close(exception): # pylint:disable=W0613
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
@templated()
@authenticated
def home():
    pass

@app.route('/gate')
@templated()
def gate():
    return dict(login_form=LoginForm(), join_form=JoinForm())

@app.route('/login', methods=['GET', 'POST'])
@templated()
def login():
    form = LoginForm(request.form)
    if request.method != 'POST' or not form.validate():
        return dict(login_form=form)
    if auth_login(session, **form.data):
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login', fail=1))

@app.route('/logout')
def logout():
    auth_logout(session)
    return redirect(url_for('gate'))

@app.route('/join', methods=['GET', 'POST'])
@templated()
def join():
    form = JoinForm(request.form)
    if request.method != 'POST' or not form.validate():
        return dict(join_form=form)
    else:
        user_id = create_user(form.nickname.data, form.password.data)
        session['user_id'] = user_id
        return redirect(url_for('home'))
