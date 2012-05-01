"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from logging import debug
from flask import g, request, session, abort
from faceoff import app
from faceoff.forms import ReportForm
from faceoff.helpers.decorators import templated, authenticated
from faceoff.models.league import find_league, get_active_leagues
from faceoff.models.user import find_user, get_active_users

@app.url_defaults
def add_league_to_url(endpoint, view_args):
    if ('league' not in view_args and 
        app.url_map.is_endpoint_expecting(endpoint, 'league') and 
        hasattr(g, 'league')):
        view_args['league'] = g.league['slug']

@app.url_value_preprocessor
def get_league_from_url(endpoint, view_args):
    if not view_args or 'league' not in view_args:
        return
    slug = view_args.pop('league')
    league = find_league(slug=slug)
    if league is None or league['active'] != 1:
        abort(404)
    g.league = league

@app.context_processor
def inject_template_data():
    data = dict(
        current_user=find_user(id=session.get('user_id')),
        active_users=get_active_users(),
        active_leagues=get_active_leagues()
        )
    if hasattr(g, 'league'):
        data['league'] = g.league
        data['report_form'] = ReportForm(data['active_users'])
    return data

@app.route('/')
@authenticated
def landing():
    return 'blah'

@app.route('/<league>/')
@templated()
@authenticated
def dashboard():
    pass

@app.route('/<league>/report')
@authenticated
def report():
    return 'foo'

@app.route('/<league>/stats/')
@templated()
@authenticated
def stats():
    pass

@app.route('/<league>/history/')
@templated()
@authenticated
def history():
    pass
