/**
 * The initial Faceoff database schema. All schema updates are incremental and
 * based on this version.
 * 
 * Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
 * License: MIT, see LICENSE for details
 */

CREATE TABLE company (
    id CHAR(32) PRIMARY KEY,
    subdomain VARCHAR(32),
    name VARCHAR(255),
    date_created DATE
    );
CREATE UNIQUE INDEX id_company_subdomain ON company (subdomain);
CREATE INDEX idx_company_search_latest ON company (date_created);

CREATE TABLE user (
    id CHAR(32) PRIMARY KEY,
    company_id INTEGER,
    nickname VARCHAR(25),
    email VARCHAR(255),
    password CHAR(40),
    salt CHAR(8),
    date_created DATE
    );
CREATE UNIQUE INDEX idx_user_unique ON user (company_id, email);
CREATE INDEX idx_user_search_nickname ON user (company_id, nickname);
CREATE INDEX idx_user_search_latest ON user (company_id, date_created);

CREATE TABLE league (
    id CHAR(32) PRIMARY KEY,
    company_id INTEGER,
    name VARCHAR(64),
    info TEXT DEFAULT NULL,
    active TINYINT(1) DEFAULT 1,
    date_created DATE
    );
CREATE INDEX idx_league_search_name ON league (company_id, name);
CREATE INDEX idx_league_search_latest  ON league (company_id, date_created);

