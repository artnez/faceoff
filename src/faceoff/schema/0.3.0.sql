/**
 * Adds `mu` and `sigma` to matches.
 * 
 * Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
 * License: MIT, see LICENSE for details
 */

ALTER TABLE ranking ADD COLUMN mu vARCHAR(64);
ALTER TABLE ranking ADD COLUMN sigma vARCHAR(64);
