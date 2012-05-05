"""
Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

from faceoff import app

def debug():
    """
    Raises an error that will trigger the Flask debugger in the browser.
    """
    assert app.debug == False
