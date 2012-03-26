"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import os
import re
from flask.sessions import SessionInterface, SessionMixin
from logging import getLogger
from hashlib import sha1
from uuid import uuid4

def init_app(app):
    """
    Binds the session manager to the provided application object.
    """
    app.session_interface = Session()

def generate_session_id(request, secret_key):
    """
    Generates a unique session ID for the given request.
    """
    secret = sha1(secret_key).hexdigest()
    unique = generate_unique_hash(request)
    return '%s_%s' % (secret, unique)

def generate_unique_hash(request):
    """
    Generates a unique hash seeded by the incoming http request.
    """
    fp = '%s %s' % (request.user_agent, request.remote_addr)
    rand = os.urandom(40).encode('hex')
    return sha1('%s_%s_%s' % (fp, rand, uuid4())).hexdigest()

def valid_session_id(session_id, secret_key):
    """
    Returns True if the given session ID is valid, False otherwise.
    """
    if re.match(r'[0-9a-z]{40}_[0-9a-z]{40}', session_id) is None:
        return False
    (secret, unique) = session_id.split('_')
    if secret != sha1(secret_key).hexdigest():
        return False
    return True

class SessionData(dict, SessionMixin):
    """
    Session data storage container. 
    """
    pass

class Session(SessionInterface):
    """
    Implements the Flask session interface to provide an alternative storage 
    model for Flask sessions. In this case, Memcached.
    """

    def __init__(self):
        self.session_id = None
        self.new_session = False
        super(Session, self).__init__()

    def getLogger(self):
        return getLogger('session')

    def open_session(self, app, request):
        """
        Loads an existing session by cookie ID. If no session with ID is found 
        or the given ID is invalid, a new session ID is created and stored.
        Returns an instance of `SessionData`
        """
        logger = self.getLogger()

        session_id = request.cookies.get(app.session_cookie_name)
        secret_key = app.config['SECRET_KEY']
        if session_id is None or not valid_session_id(session_id, secret_key):
            session_id = generate_session_id(request, secret_key)
            new_session = True
            logger.info('created new session id "%s"' % session_id)
        else:
            new_session = False
            logger.info('loaded existing session id "%s"' % session_id)

        session_data = app.cache.get(session_id)
        if session_data is None:
            logger.info('session data not found, creating new session data')
            session_data = {}
            app.cache.set(session_id, {})
        else:
            logger.info('session data loaded')

        self.session_id = session_id
        self.new_session = new_session
        return SessionData(session_data)

    def save_session(self, app, session, response):
        """
        Stores the current session data in memory. If this is a new session, a 
        cookie with the session ID is saved as well.
        """
        logger = self.getLogger()

        if self.session_id is None:
            logger.warning('attempting to save session without id')

        app.cache.set(self.session_id, session)

        if self.new_session:
            expires = self.get_expiration_time(app, session)
            domain = self.get_cookie_domain(app)
            path = self.get_cookie_path(app)
            httponly = self.get_cookie_httponly(app)
            secure = self.get_cookie_secure(app)
            response.set_cookie(app.session_cookie_name, self.session_id, 
                                path=path, expires=expires, httponly=httponly, 
                                secure=secure, domain=domain)
