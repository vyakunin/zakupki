#!/usr/bin/env python
# encoding: utf-8
"""
homepage.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""

import collections
import logging
import os

from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import model

TEMPLATE_PATH = '../templates/homepage.html'
# date format for requests
DATE_FORMAT = '%Y.%m.%d'

class HomePageView(webapp.RequestHandler):
  def get(self):
    """Implements GET request handler.

    Parameters:
      none:
    """    
    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), TEMPLATE_PATH)
    self.response.out.write(template.render(path, {}))
