"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import logging
from time import time
from faceoff.db import use_db
from faceoff.debug import debug
from trueskill import TrueSkill

@use_db
def find_match(db, **kwargs):
    return db.find('match', **kwargs)

@use_db
def search_matches(db, **kwargs):
    return db.search('match', **kwargs)

@use_db
def get_match_history(db, league_id, user_id=None, start=0, count=100):
    params = [league_id]
    query = """
        SELECT 
            match.*, winner.id AS winner_id, winner.nickname AS winner_nickname, 
            loser.id AS loser_id, loser.nickname AS loser_nickname 
        FROM match 
        INNER JOIN user AS winner ON winner.id = match.winner_id
        INNER JOIN user AS loser ON loser.id = match.loser_id
        WHERE match.league_id=? 
        """
    if user_id is not None:
        query += " AND (winner.id=? OR loser.id=?) "
        params.extend([user_id, user_id])
    query += ' ORDER BY match.date_created DESC '
    if count is not None:
        query += ' LIMIT %d, %d ' % (start, count)
    return db.select(query, params)

@use_db
def create_match(db, league_id, winner_user_id, loser_user_id, norebuild=False):
    match_id = db.insert(
        'match',
        league_id = league_id,
        winner_id = winner_user_id,
        winner_rank = get_user_rank(db, league_id, winner_user_id),
        loser_id = loser_user_id,
        loser_rank = get_user_rank(db, league_id, loser_user_id),
        date_created = int(time())
        )
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

    # generate a local player ranking profile based on user id. all matches will 
    # be traversed and this object will be populated to build the rankings.
    players = {}
    for match in search_matches(db, league_id=league_id):
        w = match['winner_id']
        l = match['loser_id']

        # create ranking profile if hasn't been added yet
        for p in [w, l]:
            if not players.has_key(p):
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
    rankings.sort(key=lambda p: p['rating'].mu-3*p['rating'].sigma)
    rankings.reverse()

    # create rankings
    for (i, r) in enumerate(rankings):
        db.execute(
            'INSERT INTO ranking (league_id, user_id, rank, wins, losses, win_streak, loss_streak, games) ' \
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
            [league_id, r['id'], (i+1), r['win'], r['loss'], r['win_streak'], r['loss_streak'], r['games']])

    if not db.is_building:
        db.commit()
