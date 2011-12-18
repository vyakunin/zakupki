#!/usr/bin/env python
# encoding: utf-8
"""
suppliers.py

Copyright (c) 2011, All its authors.
All rights reserved.
"""

import collections
import datetime
import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import model
from view import config


class SuppliersView(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/suppliers.html')
    self.response.out.write(template.render(path, {'config': config.Config}))


class SupplierView(webapp.RequestHandler):
  def GetTemplateValues(self):
    id = self.request.get('id')
    supplier = model.Supplier.get_by_key_name(id)
    return {'supplier': supplier,
            'config': config.Config}

  def get(self):
    template_values = self.GetTemplateValues()

    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/supplier.html')
    self.response.out.write(template.render(path, template_values))
