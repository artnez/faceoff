#! /usr/bin/env python

"""
Runs Faceoff as a standalone web server. Do not use this is in production.

Copyright: (c) 2012-2014 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from sys import path
from os import environ
from os.path import dirname, join

path.append(join(dirname(__file__), '..'))

from argparse import ArgumentParser
parser = ArgumentParser(usage='%(prog)s [options]', argument_default='')
parser.add_argument('--host', metavar='<string>', dest='FACEOFF_HOST', default='0')
parser.add_argument('--port', metavar='<string>', dest='FACEOFF_PORT', default='5000')
parser.add_argument('--config', metavar='<string>', dest='FACEOFF_CONFIG')
parser.add_argument('--debug', action='store_const', const='1', dest='FACEOFF_DEBUG')
parser.add_argument('--db-path', metavar='<string>', dest='FACEOFF_DB_PATH')
parser.add_argument('--db-fixtures', action='store_const', const='1', dest='FACEOFF_DB_FIXTURES')
parser.add_argument('--log-path', metavar='<string>', dest='FACEOFF_LOG_PATH')
parser.add_argument('--log-level', metavar='<string>', dest='FACEOFF_LOG_LEVEL')
parser.add_argument('--log-filter', metavar='<string>', dest='FACEOFF_LOG_FILTER')
parser.add_argument('--log-ignore', metavar='<string>', dest='FACEOFF_LOG_IGNORE')
args = parser.parse_args()
environ.update(vars(args))

from faceoff import app
app.run(args.FACEOFF_HOST, int(args.FACEOFF_PORT), threaded=True)
