"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from functools import wraps
from flask import g, request, session, render_template, url_for, redirect

def templated(template_name=None):
    """
    Automatically renders a template named after the current endpoint. Will also
    render the name provided if given.
    """
    def closure(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            template = template_name
            response = f(*args, **kwargs)
            if response is None:
                response = {}
            elif not isinstance(response, dict):
                return response
            if template is None:
                template = '%s.html' % request.endpoint
            return render_template(template, **response)
        return decorator
    return closure

def authenticated(f):
    """
    Asserts that an existing logged-in user session is active. If not, redirects
    to the authenticate gate.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('gate'))
        return f(*args, **kwargs)
    return decorator
