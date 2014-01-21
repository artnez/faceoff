/**
 * Adds `mu` and `sigma` to matches.
 * 
 * Copyright: (c) 2012-2014 Artem Nezvigin <artem@artnez.com>
 * License: MIT, see LICENSE for details
 */

ALTER TABLE ranking ADD COLUMN mu VARCHAR(64);
ALTER TABLE ranking ADD COLUMN sigma VARCHAR(64);
UPDATE setting SET value='1.1' WHERE name='schema_version';
