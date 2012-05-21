"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os
import logging
from datetime import datetime
from time import localtime, strftime
from flask import \
    g, request, session, flash, abort, redirect, url_for, send_from_directory
from faceoff import app
from faceoff.debug import debug
from faceoff.forms import \
    LoginForm, JoinForm, ReportForm, NewLeagueForm, SettingsForm, ProfileForm, \
    ConfigForm
from faceoff.helpers.decorators import authenticated, templated
from faceoff.models.user import \
    get_active_users, create_user, update_user, auth_login, auth_logout
from faceoff.models.league import \
    find_league, get_active_leagues, get_inactive_leagues, create_league, \
    update_league
from faceoff.models.match import \
    create_match, get_match_history, get_league_ranking, get_user_standing, \
    rebuild_rankings
from faceoff.models.setting import get_setting, del_setting, set_setting

@app.teardown_request
def db_close(exception): # pylint:disable=W0613
    if hasattr(g, 'db'):
        g.db.close()

@app.url_value_preprocessor
def get_league_from_url(endpoint, view_args):
    if not view_args or 'league' not in view_args:
        return
    league = find_league(slug=view_args.pop('league'))
    if league is None:
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

@app.template_filter('date_format')
def date_format(s, f):
    return strftime(f, localtime(int(s)))

@app.template_filter('player_rank')
def player_rank(r):
    return '---' if r is None else '%03d' % int(r)

@app.template_filter('human_date')
def human_date(s):
    d = datetime.fromtimestamp(s)
    n = datetime.today()
    if d.date() == n.date():
        return 'today @ %s' % d.strftime('%-I:%M %p').lower()
    x = n - d
    if x.days == 1:
        return 'yesterday @ %s' % d.strftime('%-I:%M %p').lower()
    if d.year == n.year:
        return d.strftime('%a, %b %-d'+num_suffix(d.day)) + \
               d.strftime(' @ %-I%p').lower()
    return d.strftime('%b %-d'+num_suffix(d.day)+', %Y')+ \
           d.strftime(' @ %-I%p').lower()

@app.template_filter('num_suffix')
def num_suffix(d):
    return 'th' if 11 <= d <= 13 else {1:'st', 2:'nd', 3:'rd'}.get(d % 10, 'th')

@app.route('/favicon.ico')
def favicon():
    path = os.path.join(app.root_path, 'static')
    return send_from_directory(path, 'favicon.ico')

@app.route('/gate')
@templated()
def gate():
    join_form = JoinForm(access_code=get_setting('access_code'))
    return dict(login_form=LoginForm(), join_form=join_form)

@app.route('/login', methods=('GET', 'POST'))
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

@app.route('/join', methods=('GET', 'POST'))
@templated()
def join():
    form = JoinForm(request.form, access_code=get_setting('access_code'))
    if request.method != 'POST' or not form.validate():
        return dict(join_form=form)
    user_id = create_user(form.nickname.data, form.password.data)
    session['user_id'] = user_id
    return redirect(url_for('landing'))

@app.route('/')
@templated()
@authenticated
def landing():
    return dict(active_leagues=get_active_leagues())

@app.route('/profile', methods=('GET', 'POST'))
@templated()
@authenticated
def profile():
    form = ProfileForm(request.form)
    if request.method == 'POST' and form.validate():
        update_user(
            g.current_user['id'],
            nickname = form.nickname.data,
            password = form.password.data
            )
        flash('Profile updated successfully!')
        return redirect(url_for('landing'))
    form.nickname.data = g.current_user['nickname']
    return dict(profile_form=form)

@app.route('/inactive')
@templated()
@authenticated
def inactive():
    return dict(inactive_leagues=get_inactive_leagues())

@app.route('/new', methods=('GET', 'POST'))
@templated()
@authenticated
def new_league():
    form = NewLeagueForm(request.form)
    if request.method != 'POST' or not form.validate():
        return dict(new_league_form=form)
    create_league(form.name.data) 
    return redirect(url_for('landing'))

@app.route('/config', methods=('GET', 'POST'))
@templated()
@authenticated
def config():
    form = ConfigForm(request.form)
    if request.method != 'POST' or not form.validate():
        form.access_code.data = get_setting('access_code')
        return dict(config_form=form)
    access_code = form.access_code.data.strip()
    if access_code == '':
        del_setting('access_code')
        flash('Access code removed')
    else:
        set_setting('access_code', access_code)
        flash('Access changed')
    return redirect(url_for('config'))

@app.route('/<league>/')
@templated()
@authenticated
def dashboard():
    user = g.current_user
    league = g.current_league
    return dict(
        report_form = ReportForm(get_active_users()),
        current_ranking = get_user_standing(league['id'], user['id']),
        ranking=get_league_ranking(league['id']),
        history=get_match_history(league['id'], user_id=user['id'])
        )

@app.route('/<league>/report', methods=('POST',))
@templated()
@authenticated
def report():
    if not g.current_league['active']:
        abort(403)
    form = ReportForm(get_active_users(), request.form)
    if not form.validate():
        return dict(form=form)
    is_win = form.result.data == '1'
    cur_user = g.current_user['id']
    opp_user = form.opponent.data
    (winner, loser) = (cur_user, opp_user) if is_win else (opp_user, cur_user)
    create_match(g.current_league['id'], winner, loser)
    return redirect(url_for('dashboard'))

@app.route('/<league>/standings/')
@templated()
@authenticated
def standings():
    return dict(ranking=get_league_ranking(g.current_league['id']))

@app.route('/<league>/history/')
@templated()
@authenticated
def history():
    return dict(match_history=get_match_history(g.current_league['id']))

@app.route('/<league>/settings/', methods=('GET', 'POST'))
@templated()
@authenticated
def settings():
    league = g.current_league
    form = SettingsForm(request.form)
    if request.method != 'POST':
        form.name.data = g.current_league['name']
        form.active.data = '1' if g.current_league['active'] else '0'
        return dict(settings_form=form)
    if form.validate():
        league = update_league(
            league['id'], 
            name = form.name.data, 
            active = True if form.active.data == '1' else False
            )
        flash('League settings updated')
        return redirect(url_for('settings', league=league['slug']))
    return dict(settings_form=form)

@app.route('/<league>/rebuild/', methods=('POST',))
@templated()
@authenticated
def rebuild():
    flash('Standings rebuild complete')
    rebuild_rankings(g.current_league['id'])
    return redirect(url_for('settings'))
