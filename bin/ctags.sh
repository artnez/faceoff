#! /usr/bin/env bash
#
# Generates a ctags tag file for this project. Tries to include all libraries
# in the default PYTHONPATH as well.
#
# Requires Exuberant Ctags (http://ctags.sourceforge.net). GNU Ctags won't work.
#
# Author: Artem Nezvigin <artem@artnez.com>
# License: MIT, see LICENSE for details

CTAGS_VERSION=$(ctags --version 2> /dev/null | sed 's/^ *//;s/ *$//')
if [ "$CTAGS_VERSION" = "" ]; then
    echo "Not using excuberant ctags!" >&2
    exit 1
fi

PROJECT=$(cd `dirname $0`/../ && pwd)
PYTHON=$(python -c "import sys; print(' '.join(sys.path))")
ctags --recurse \
      --totals \
      --languages='Python,JavaScript' \
      $@ \
      $PROJECT \
      $PYTHON

