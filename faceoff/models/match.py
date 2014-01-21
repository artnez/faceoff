"""
Copyright: (c) 2012-2014 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from time import time
from datetime import datetime
from faceoff.db import use_db
from trueskill import TrueSkill


@use_db
def find_match(db, **kwargs):
    return db.find('match', **kwargs)


@use_db
def search_matches(db, league_id, user_id=None, time_start=None, time_end=None,
                   page=None, per_page=10, sort='date_created', order='desc'):
    params = [league_id]
    fields = """
        match.*, winner.id AS winner_id, winner.nickname AS winner_nickname,
        loser.id AS loser_id, loser.nickname AS loser_nickname
        """
    query = """
        FROM match
        INNER JOIN user AS winner ON winner.id = match.winner_id
        INNER JOIN user AS loser ON loser.id = match.loser_id
        WHERE match.league_id=?
        """
    if user_id is not None:
        query += " AND (winner.id=? OR loser.id=?) "
        params.extend([user_id, user_id])
    if time_start is not None:
        query += " AND match.date_created >= ? "
        params.append(time_start)
    if time_end is not None:
        query += " AND match.date_created <= ? "
        params.append(time_end)
    query += ' ORDER BY match.%s %s ' % (db.clean(sort), db.clean(order))
    if page is not None and page > 0:
        return db.paginate(fields, query, params, page, per_page)
    else:
        return db.select("SELECT %s %s" % (fields, query), params)


@use_db
def find_older_match(db, league_id, user_id, timestamp):
    result = search_matches(
        db, league_id, user_id=user_id, time_end=timestamp, page=1, per_page=1
        )
    if not len(result['row_data']):
        return None
    match = result['row_data'][0]
    match['date'] = datetime.fromtimestamp(match['date_created'])
    match['dateargs'] = {
        'year': match['date'].year,
        'month': match['date'].strftime('%b').lower(),
        'day': match['date'].day
        }
    return match


@use_db
def find_newer_match(db, league_id, user_id, timestamp):
    result = search_matches(
        db, league_id, user_id=user_id, time_start=timestamp, page=1,
        per_page=1, order='asc')
    if not len(result['row_data']):
        return None
    match = result['row_data'][0]
    match['date'] = datetime.fromtimestamp(match['date_created'])
    match['dateargs'] = {
        'year': match['date'].year,
        'month': match['date'].strftime('%b').lower(),
        'day': match['date'].day
        }
    return match


@use_db
def create_match(db, league_id, winner_user_id, loser_user_id, match_date=None,
                 norebuild=False):
    match_id = db.insert(
        'match',
        league_id=league_id,
        winner_id=winner_user_id,
        winner_rank=get_user_rank(db, league_id, winner_user_id),
        loser_id=loser_user_id,
        loser_rank=get_user_rank(db, league_id, loser_user_id),
        date_created=int(time()) if match_date is None else match_date)
    if not norebuild:
        rebuild_rankings(db, league_id)
    return match_id


@use_db
def get_league_ranking(db, league_id):
    return db.select("""
        SELECT ranking.*, user.nickname
        FROM ranking
        INNER JOIN user ON user.id=ranking.user_id
        WHERE ranking.league_id=?
        ORDER BY ranking.rank ASC
        """, [league_id])


@use_db
def get_user_rank(db, league_id, user_id):
    rank = db.find('ranking', league_id=league_id, user_id=user_id)
    return None if rank is None else rank['rank']


@use_db
def get_user_standing(db, league_id, user_id):
    return db.find('ranking', league_id=league_id, user_id=user_id)


@use_db
def rebuild_rankings(db, league_id):
    # exclusive lock is needed to prevent race conditions when multiple people
    # are simultaneously reporting a match.
    if not db.is_building:
        db.execute('begin exclusive')

    # delete all existing rankings
    db.execute('DELETE FROM ranking WHERE league_id=?', [league_id])

    skill = TrueSkill()

    # generate a local player ranking profile based on user id. all matches
    # will be traversed and this object will be populated to build the
    # rankings.
    players = {}
    for match in db.search('match', league_id=league_id):
        w = match['winner_id']
        l = match['loser_id']

        # create ranking profile if hasn't been added yet
        for p in [w, l]:
            if not p in players:
                players[p] = {
                    'id': p, 'win': 0, 'loss': 0, 'win_streak': 0,
                    'loss_streak': 0, 'games': 0, 'rating': skill.Rating()}

        # define ranking profile properties, this will go into the db and will
        # be viewable on the standings page
        players[w]['games'] += 1
        players[w]['win'] += 1
        players[w]['win_streak'] += 1
        players[w]['loss_streak'] = 0
        players[l]['games'] += 1
        players[l]['loss'] += 1
        players[l]['win_streak'] = 0
        players[l]['loss_streak'] += 1

        # finally, record the match with trueskill and let it calculate ranks
        wr = players[w]['rating']
        lr = players[l]['rating']
        (wr, lr) = skill.transform_ratings([(wr,), (lr,)])
        players[w]['rating'] = wr[0]
        players[l]['rating'] = lr[0]

    # sort the players based on their ranking
    rankings = [p for p in players.values()]
    rankings.sort(key=lambda p: p['rating'].exposure)
    rankings.reverse()

    # create rankings
    for (i, r) in enumerate(rankings):
        fields = {
            'league_id': league_id, 'user_id': r['id'], 'rank': (i+1),
            'mu': r['rating'].mu, 'sigma': r['rating'].sigma, 'wins': r['win'],
            'losses': r['loss'], 'win_streak': r['win_streak'],
            'loss_streak': r['loss_streak'], 'games': r['games']
            }
        db.insert('ranking', pk=False, **fields)

    if not db.is_building:
        db.commit()
