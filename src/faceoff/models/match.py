"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import logging
from time import time
from faceoff.db import use_db
from faceoff.debug import debug
from trueskill import Rating

@use_db
def find_match(db, **kwargs):
    return db.find('match', **kwargs)

@use_db
def search_matches(db, **kwargs):
    return db.search('match', **kwargs)

@use_db
def get_match_history(db, league_id, start=0, count=100):
    query = """
        SELECT 
            match.*, winner.id AS winner_id, winner.nickname AS winner_nickname, 
            loser.id AS loser_id, loser.nickname AS loser_nickname 
        FROM match 
        INNER JOIN user AS winner ON winner.id = match.winner_id
        INNER JOIN user AS loser ON loser.id = match.loser_id
        WHERE match.league_id=? 
        ORDER BY match.date_created DESC
        LIMIT %d, %d
        """ % (start, count)
    return db.select(query, [league_id])

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
        ORDER BY ranking.rank DESC
        """, [league_id])

@use_db
def get_user_rank(db, league_id, user_id):
    rank = db.find('ranking', league_id=league_id, user_id=user_id)
    return None if rank is None else rank['rank']

@use_db
def rebuild_rankings(db, league_id):
    # exclusive lock is needed to prevent race conditions when multiple people
    # are simultaneously reporting a match.
    if not db.is_building:
        db.execute('begin exclusive')

    # delete all existing rankings
    db.execute('DELETE FROM ranking WHERE league_id=?', [league_id])

    # generate a local player ranking profile based on user id. all matches will 
    # be traversed and this object will be populated to build the rankings.
    profiles = {}
    for match in search_matches(db, league_id=league_id):
        w = match['winner_id']
        if not profiles.has_key(w):
            profiles[w] = {
                'id': w, 'rank': 0, 'win': 0, 'loss': 0, 'win_streak': 0, 
                'loss_streak': 0, 'games': 0}
        l = match['loser_id']
        if not profiles.has_key(l):
            profiles[l] = {
                'id': l, 'rank': 0, 'win': 0, 'loss': 0, 'win_streak': 0, 
                'loss_streak': 0, 'games': 0}
        profiles[w]['games'] += 1
        profiles[w]['win'] += 1
        profiles[w]['win_streak'] += 1
        profiles[w]['loss_streak'] = 0
        profiles[l]['games'] += 1
        profiles[l]['loss'] += 1
        profiles[l]['win_streak'] = 0
        profiles[l]['loss_streak'] += 1

    # create rankings
    for p in profiles.values():
        db.execute(
            'INSERT INTO ranking (league_id, user_id, rank, wins, losses, ' \
                                 'win_streak, loss_streak, games) ' \
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
            [league_id, p['id'], p['rank'], p['win'], p['loss'], p['win_streak'], 
             p['loss_streak'], p['games']]
            )

    if not db.is_building:
        db.commit()
