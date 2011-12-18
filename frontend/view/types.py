#!/usr/bin/env python
# encoding: utf-8
"""
types.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""

import os

from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import model
from view import config


class TypesView(webapp.RequestHandler):
  """Renders types page."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/types.html')
    self.response.out.write(template.render(path, {'config': config.Config}))
