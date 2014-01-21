"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from functools import wraps
from flask import g, request, session, render_template, url_for, redirect
from faceoff.models.user import find_user


def templated(template_name=None):
    """
    Automatically renders a template named after the current endpoint. Will
    also render the name provided if given.
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
    Asserts that an existing logged-in user session is active. If not,
    redirects to the authenticate gate.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is None:
            return redirect(url_for('gate'))
        user = find_user(id=user_id)
        if user is None:
            return redirect(url_for('gate'))
        g.current_user = user
        return f(*args, **kwargs)
    return decorator
