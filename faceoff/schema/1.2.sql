/**
 * Adds detailed stats to match history.
 * 
 * Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
 * License: MIT, see LICENSE for details
 */

ALTER TABLE match ADD COLUMN draw_prob VARCHAR(64);
ALTER TABLE match ADD COLUMN winner_mu VARCHAR(64);
ALTER TABLE match ADD COLUMN winner_sigma VARCHAR(64);
ALTER TABLE match ADD COLUMN loser_mu VARCHAR(64);
ALTER TABLE match ADD COLUMN loser_sigma VARCHAR(64);
UPDATE setting SET value='1.2' WHERE name='schema_version';
