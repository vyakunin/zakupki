#!/usr/bin/env python
# encoding: utf-8
"""
customers.py

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

CUSTOMER_HTML_TEMPLATE_PATH = '../templates/customer.html'
JSON_TEMPLATE_PATH = '../templates/customers.json'
DATE_FORMAT = '%Y.%m.%d'


class CustomerView(webapp.RequestHandler):
  def GetTemplateValues(self):
    id = self.request.get('id')
    customer = model.Customer.get_by_key_name(id)
    return {'customer': customer}

  def get(self):
    template_values = self.GetTemplateValues()

    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), CUSTOMER_HTML_TEMPLATE_PATH)
    self.response.out.write(template.render(path, template_values))
