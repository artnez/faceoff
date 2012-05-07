#! /usr/bin/env python

"""
Runs Faceoff in a WSGI environment.

Copyright: (c) 2012 Artem Nezvigin <artem@artnez.com>
License: MIT, see LICENSE for details
"""

import sys
import os

project_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(project_dir, 'src'))
sys.path.insert(1, os.path.join(project_dir, 'lib'))

from faceoff import app as application
