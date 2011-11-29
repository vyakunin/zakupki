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

SUPPLIER_HTML_TEMPLATE_PATH = '../templates/supplier.html'


class SupplierView(webapp.RequestHandler):
  def GetTemplateValues(self):
    id = self.request.get('id')
    supplier = model.Supplier.get_by_key_name(id)
    return {'supplier': supplier}

  def get(self):
    template_values = self.GetTemplateValues()

    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), SUPPLIER_HTML_TEMPLATE_PATH)
    self.response.out.write(template.render(path, template_values))
