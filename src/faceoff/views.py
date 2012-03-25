"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from flask import Flask, g, request, abort, redirect, url_for, session
from faceoff import app
from faceoff.models import UserModel
from faceoff.forms import LoginForm, JoinForm
from faceoff.helpers.decorators import templated, authenticated

@app.before_request
def db_open():
    g.db = app.db.connect()

@app.teardown_request
def db_close(exception): # pylint:disable=W0613
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
    if UserModel(g.db).login(session, **form.data):
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login', fail=1))

@app.route('/logout')
def logout():
    UserModel(g.db).logout(session)
    return redirect(url_for('gate'))

@app.route('/join', methods=['GET', 'POST'])
@templated()
def join():
    form = JoinForm(request.form)
    if request.method != 'POST' or not form.validate():
        return dict(join_form=form)
    user_model = UserModel(g.db)
    user = user_model.find(nickname=form.nickname.data)
    if user is not None:
        return redirect(url_for('join', dup=1))
    else:
        user_id = user_model.create(form.nickname.data, form.password.data)
        session['user_id'] = user_id
        return redirect(url_for('home'))
