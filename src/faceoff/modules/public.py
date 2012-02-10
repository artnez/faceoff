"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from flask import Blueprint
from faceoff.helpers.decorators import templated

__all__ = ['module']

module = Blueprint('public', __name__, static_folder='static')

@module.route('/')
@templated()
def home():
    pass

