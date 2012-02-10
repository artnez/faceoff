"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from functools import wraps
from flask import request, render_template

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
                template = 'pages/%s.html' % request.endpoint
            return render_template(template, **response)
        return decorator
    return closure

