/**
 * The initial Faceoff database schema. All schema updates are incremental and
 * based on this version.
 * 
 * Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
 * License: MIT, see LICENSE for details
 */

CREATE TABLE settings (
    name CHAR(32) PRIMARY KEY,
    value TEXT DEFAULT NULL
    );

CREATE TABLE user (
    id CHAR(32) PRIMARY KEY,
    nickname VARCHAR(25),
    password CHAR(40),
    salt CHAR(8),
    date_created DATE
    );
CREATE UNIQUE INDEX idx_user_unique ON user (nickname);
CREATE INDEX idx_user_newest ON user (date_created);

CREATE TABLE league (
    id CHAR(32) PRIMARY KEY,
    name VARCHAR(64),
    description TEXT DEFAULT NULL,
    active TINYINT(1) DEFAULT 1,
    date_created DATE
    );
CREATE INDEX idx_league_name ON league (name);
CREATE INDEX idx_league_newest ON league (date_created);

