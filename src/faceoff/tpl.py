"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from datetime import datetime
from time import localtime, strftime

_filters = {}

def init_app(app):
    app.jinja_env.filters.update(_filters)

def template_filter(f):
    """
    Marks the decorated function as a template filter.
    """
    _filters[f.__name__] = f

@template_filter
def date_format(s, f):
    return strftime(f, localtime(int(s)))

@template_filter
def player_rank(r):
    return '---' if r is None else '%03d' % int(r)

@template_filter
def human_date(s):
    d = datetime.fromtimestamp(s)
    n = datetime.today()
    if d.date() == n.date():
        return 'today @ %s' % d.strftime('%-I:%M %p').lower()
    x = n - d
    if x.days == 1:
        return 'yesterday @ %s' % d.strftime('%-I:%M %p').lower()
    if d.year == n.year:
        return d.strftime('%a, %b %-d'+num_suffix(d.day)) + \
               d.strftime(' @ %-I%p').lower()
    return d.strftime('%b %-d'+num_suffix(d.day)+', %Y')+ \
           d.strftime(' @ %-I%p').lower()

@template_filter
def num_suffix(d):
    return 'th' if 11 <= d <= 13 else {1:'st', 2:'nd', 3:'rd'}.get(d % 10, 'th')
