#!/usr/bin/env python
# encoding: utf-8
"""
homepage.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import model
from view import config


class AboutView(webapp.RequestHandler):
  """Renders homepage."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/about.html')
    self.response.out.write(template.render(path, {'config': config.Config}))


class HomePageView(webapp.RequestHandler):
  """Renders homepage."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/homepage.html')
    self.response.out.write(template.render(path, {'config': config.Config}))
