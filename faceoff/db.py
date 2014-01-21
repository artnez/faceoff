"""
Copyright: (c) 2012-2014 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os
import re
import sqlite3
import atexit
import string
import logging
from math import ceil
from threading import current_thread
from tempfile import gettempdir
from contextlib import closing
from glob import glob
from uuid import uuid4, uuid5
from hashlib import sha1
from random import random, shuffle
from time import time
from natsort import natsorted
from functools import wraps

_curdir = os.path.dirname(__file__)
_schema = os.path.join(_curdir, 'schema')
_global_factory = None


def init_app(app):
    """
    Configures the provided app's database connection layer. Attaches a `db`
    property to the app object that will act as a database connection factory
    for the application's threads and subprocesses to use.
    """
    db_path = app.config['DB_PATH']
    if db_path:
        db_path = os.path.expanduser(db_path)
        if not os.path.exists(db_path):
            db_path = make_new_db(db_path)
    else:
        db_path = make_temp_db()
    app.db = Factory(db_path)
    set_global_factory(app.db)


def make_temp_db():
    """
    Creates a temporary database file and deletes when the process is ends.
    Returns the path to the temporary file.
    """
    db_link = os.path.expanduser(os.path.join('~', '.faceoff.tmp.db'))
    if not os.path.exists(db_link):
        pid, tid = os.getpid(), current_thread().ident
        db_path = os.path.join(gettempdir(), 'faceoff%s%s.tmp.db' % (pid, tid))
        build_schema(db_path, _schema)
        os.symlink(db_path, db_link)
        atexit.register(clean_temp_db(db_path, db_link))
        logger().info('created tmp db at %s linked by %s' % (db_path, db_link))
    return db_link


def clean_temp_db(db_path, db_link):
    """
    Returns a closed function that deletes the temporary database file at
    the given path.
    """
    def cleaner():
        logger().info('cleanup temp db file %s' % db_path)
        os.remove(db_path)
        logger().info('cleanup temp db link %s' % db_link)
        os.remove(db_link)
    return cleaner


def make_new_db(path):
    """
    Creates a new database at the given location.
    """
    build_schema(path, _schema)
    logger().info('created fresh db %s' % path)
    return path


def build_schema(db_path, schema_path):
    """
    Rebuilds the database using the given schema directory.
    """
    with closing(sqlite3.connect(db_path)) as conn:
        conn.executescript(get_schema_sql(schema_path))


def get_schema_files(schema_path):
    """
    Returns a list of schema SQL files, sorted by version number.
    """
    files = glob(os.path.join(schema_path, '*.sql'))
    return natsorted(files)


def get_schema_sql(schema_path):
    """
    Concatenates all schema files into a single script for running.
    """
    scripts = []
    for path in get_schema_files(schema_path):
        with open(path) as f:
            scripts.append(f.read().strip())
    return '\n'.join(scripts)


def logger(name='db.general'):
    """
    Log into the internal database logger.
    """
    return logging.getLogger(name)


def use_db(f):
    """
    Decorator that wraps functions and inserts a global database object as
    first parameter.
    """
    varnames = f.func_code.co_varnames
    has_self = len(varnames) > 0 and varnames[0] == 'self'

    @wraps(f)
    def decorator(*args, **kwargs):
        if len(args) > 0 and isinstance(args[0], Connection):
            return f(*args, **kwargs)
        if 'db' in kwargs:
            db = get_connection(kwargs['db'])
            del kwargs['db']
        else:
            db = get_connection()
        if has_self:
            args = (args[0], db) + args[1:]
        else:
            args = (db,) + args
        return f(*args, **kwargs)
    return decorator


def get_connection(conn=None):
    """
    Attempts to load a database connection object. If a valid connection object
    is provided explicitly, it is used. If not, an attempt is made to load the
    connection from the flask global registry.
    """
    if conn:
        return conn
    from flask import g
    if not hasattr(g, 'db'):
        g.db = get_global_factory().connect()
    return g.db


def get_global_factory():
    """
    Returns the global connection factory. Use `set_global_factory` to set this
    value at some point when the application initializes.
    """
    return _global_factory


def set_global_factory(factory):
    """
    Sets the global database connection factory. This factory is used to create
    new database connections on demand.
    """
    global _global_factory
    _global_factory = factory


class Factory(object):
    """
    Database connection factory. Stores database configuration settings and
    creates new database connections.
    """

    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self, **options):
        opts = self.default_options()
        opts.update(options)
        conn = sqlite3.connect(self.db_path, factory=Connection, **opts)
        conn.row_factory = sqlite3.Row
        return conn

    def default_options(self):
        return {'isolation_level': None}


class Connection(sqlite3.Connection):
    """
    Wraps the native database connection object to provide logging ability as
    well as some helper functions to make querying more concise.
    """

    def __init__(self, *args, **kwargs):
        self.ident = self._ident(args[0])
        self._log('connect %s' % args[0])
        self.is_building = False
        sqlite3.Connection.__init__(self, *args, **kwargs)

    def find(self, table, pk=None, sort=None, order=None, **where):
        """
        Searches `table` for the given criteria and returns the first available
        record. If no records found, None is returned.
        """
        if pk:
            where['id'] = pk
        rows = self.search(table, sort=sort, order=order, limit=1, **where)
        return rows[0] if rows else None

    def search(self, table, sort=None, order=None, limit=None, **where):
        """
        Searches `table` for the given criteria and returns all matching
        records. If no records found, an empty list is returned.
        """
        query = 'SELECT * FROM "%s"' % self.clean(table)
        param = []
        if len(where):
            fields = []
            for name, value in where.iteritems():
                name = self.clean(name)
                if isinstance(value, list):
                    values = '","'.join(value)
                    fields.append('"%s" IN ("%s")' % (name, values))
                else:
                    fields.append('"%s"=?' % name)
                    param.append(value)
            query += ' WHERE ' + ' AND '.join(fields)
        if sort is not None:
            if not isinstance(sort, Expr):
                sort = '"%s"' % self.clean(sort)
            sort = str(sort)
            if order != 'asc':
                order = 'desc'
            query += ' ORDER BY %s %s' % (sort, order)
        if limit is not None:
            query += ' LIMIT %d ' % int(limit)
        c = self.execute(query, param)
        rows = []
        [rows.append(dict(zip(row.keys(), row))) for row in c.fetchall()]
        c.close()
        return rows

    def insert(self, table, pk=None, **fields):
        """
        Creates a record with primary key `pk` in `table` with the given data.
        If no `pk` is specified, it is uniquely generated.
        """
        if pk is not False:
            fields['id'] = pk or self.generate_pk(table)
        query = 'INSERT INTO "%(table)s" ("%(names)s") VALUES (%(param)s)' % {
            'table': self.clean(table),
            'names': '","'.join(map(self.clean, fields.keys())),
            'param': ','.join(['?'] * len(fields))}
        self.execute(query, fields.values())
        return fields['id'] if 'id' in fields else True

    def update(self, table, pk, **fields):
        """
        Updates a record with primary key `pk` in `table` with the given data.
        """
        if not len(fields):
            return
        query = 'UPDATE "%(table)s" SET %(pairs)s WHERE "id"=?' % {
            'table': self.clean(table),
            'pairs': ','.join([
                '"%s"=?' % self.clean(n) for n in fields.keys()])}
        self.execute(query, fields.values() + [pk])

    def delete(self, table, pk):
        """
        Deletes a record by primary key `pk` on the given `table`.
        """
        self.execute('DELETE FROM "%s" WHERE "id"=?' % table, [pk])

    def select(self, query, param):
        """
        Runs a select query and returns the entire result set.
        """
        cursor = self.execute(query, param)
        rows = []
        [rows.append(dict(zip(row.keys(), row))) for row in cursor.fetchall()]
        cursor.close()
        return rows

    def truncate_table(self, table):
        """
        Deletes all records in `table`.
        """
        self.execute('DELETE FROM "%s"' % table)

    def generate_pk(self, table):
        """
        Returns a new primary key that is guaranteed to be unique. A version 5
        UUID is generated and returned as a 32 character hex string.
        """
        return uuid5(uuid4(), table).hex

    def generate_slug(self, table, field='slug', length=4):
        """
        Returns a new unique slug for the given table name.
        """
        chars = list(string.ascii_lowercase + string.digits)
        while True:
            shuffle(chars)
            slug = ''.join(chars[0:length])
            if self.find(table, **{field: slug}) is None:
                break
        return slug

    def clean(self, string):
        """
        Enforces a strict naming convention to prevent SQL injection. This
        should be used when SQL identifiers (eg: table name, column name, etc)
        come from an untrusted source.
        """
        return re.sub(r'[^\w]', '', string)

    def cursor(self, cursorClass=None):
        return sqlite3.Connection.cursor(self, cursorClass or Cursor)

    def commit(self, *args, **kwargs):
        self._log('commit')
        return sqlite3.Connection.commit(self, *args, **kwargs)

    def rollback(self, *args, **kwargs):
        self._log('rollback')
        return sqlite3.Connection.rollback(self, *args, **kwargs)

    def close(self, *args, **kwargs):
        self._log('close')
        return sqlite3.Connection.close(self, *args, **kwargs)

    def paginate(self, cols, sql, params, page, limit):
        offset = (page - 1) * limit
        totals_query = "SELECT COUNT(*) as `count` %s " % sql
        result_query = "SELECT %s %s LIMIT %d, %d" % (cols, sql, offset, limit)
        total_rows = self.execute(totals_query, params).fetchone()['count']
        result = self.select(result_query, params)
        next_page = page + 1
        total_pages = int(ceil(total_rows / float(limit)))
        return {
            'row_data': result,
            'total_rows': total_rows,
            'total_pages': total_pages,
            'rows_per_page': limit,
            'prev_page': None if page is 1 else page - 1,
            'next_page': None if next_page > total_pages else next_page}

    def _ident(self, path):
        """
        Generates a unique connection ID that will help identify connection
        patterns in log files.
        """
        tid, pid, rand, ts = (
            current_thread().ident, os.getpid(), random(), time())
        ident = '%s_%s_%s_%s_%s' % (tid, pid, rand, ts, path)
        return sha1(ident).hexdigest()

    def _log(self, message, level='debug'):
        message = '[%s] %s' % (self.ident, message)
        getattr(logger('db.query'), level)(message)


class Cursor(sqlite3.Cursor):
    """
    Wraps the native database cursor object to provide logging ability.
    """

    def execute(self, sql, *args, **kwargs):
        self._log('execute: %s' % sql)
        return sqlite3.Cursor.execute(self, sql, *args, **kwargs)

    def executemany(self, sql, *args):
        self._log('executemany: %s' % sql)
        return sqlite3.Cursor.executemany(self, sql, *args)

    def executescript(self, sql):
        self._log('executescript: %s' % sql)
        return sqlite3.Cursor.executescript(self, sql)

    def fetchone(self):
        self._log('fetchone')
        return sqlite3.Cursor.fetchone(self)

    def fetchmany(self, *args, **kwargs):
        self._log('fetchmany')
        return sqlite3.Cursor.fetchmany(self, *args, **kwargs)

    def fetchall(self):
        self._log('fetchall')
        return sqlite3.Cursor.fetchall(self)

    def _log(self, *args, **kwargs):
        """ Proxy all logs to the connection logger. """
        self.connection._log(*args, **kwargs)  # pylint: disable=E1101


class Expr(object):
    """
    Represents a raw SQL expression. Useful when trying to differentiate user
    input from internally generated SQL code.
    """

    def __init__(self, sql):
        self.sql = sql

    def __str__(self):
        return self.sql
