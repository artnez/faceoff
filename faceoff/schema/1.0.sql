/**
 * The initial Faceoff database schema. All schema updates are incremental and
 * based on this version.
 * 
 * Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
 * License: MIT, see LICENSE for details
 */

CREATE TABLE setting (
    name CHAR(32) PRIMARY KEY,
    value TEXT DEFAULT NULL
    );
CREATE UNIQUE INDEX idx_setting_unique ON setting (name);
INSERT INTO setting (name, value) VALUES ('schema_version', '1.0');

CREATE TABLE user (
    id CHAR(32) PRIMARY KEY,
    nickname VARCHAR(25),
    password CHAR(40),
    salt CHAR(8),
    rank VARCHAR(16),
    date_created INT(11)
    );
CREATE UNIQUE INDEX idx_user_unique ON user (nickname);
CREATE INDEX idx_user_newest ON user (date_created);

CREATE TABLE league (
    id CHAR(32) PRIMARY KEY,
    slug CHAR(64),
    name VARCHAR(64),
    description TEXT DEFAULT NULL,
    active TINYINT(1) DEFAULT 1,
    date_created INT(11)
    );
CREATE INDEX idx_league_slug ON league (slug);
CREATE INDEX idx_league_newest ON league (date_created);

CREATE TABLE match (
    id CHAR(32) PRIMARY KEY,
    league_id CHAR(32),
    winner_id CHAR(32),
    winner_rank CHAR(32) DEFAULT NULL,
    loser_id CHAR(32),
    loser_rank CHAR(32) DEFAULT NULL,
    date_created INT(11)
    );
CREATE INDEX idx_match_newest ON match (date_created);
CREATE INDEX idx_match_winner_loser ON match (winner_id, loser_id);
CREATE INDEX idx_match_loser_winner ON match (loser_id, winner_id);

CREATE TABLE ranking (
    league_id CHAR(32),
    user_id CHAR(32),
    rank INT(4),
    wins INT(5),
    losses INT(5),
    win_streak INT(5),
    loss_streak INT(5),
    games INT(6),
    PRIMARY KEY (league_id, user_id)
    );
CREATE INDEX idx_ranking_league_best ON ranking (league_id, rank);
