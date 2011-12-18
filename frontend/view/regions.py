#!/usr/bin/env python
# encoding: utf-8
"""
regions.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""

import collections
import datetime
import logging
import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import model
from util import product_util
from util import region_util
from view import config


class RegionsView(webapp.RequestHandler):
  """Renders view of all the regions"""
  def get(self):
    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/regions.html')
    self.response.out.write(template.render(path, {'config': config.Config}))


class RegionView(webapp.RequestHandler):
  """Render view for one selected region."""
  
  def GetTemplateValues(self):
    code = self.request.get('code')
    return {'region_name': region_util.names.get(code, 'Unknown'),
            'region_code': code,
            'config': config.Config}
  
  def get(self):
    region = self.request.get('code')
    if not region:
      self.response.set_status(404)
      return
    
    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/region.html')
    self.response.out.write(template.render(path, 
                                            self.GetTemplateValues()))
