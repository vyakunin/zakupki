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
from view import config


class CustomersView(webapp.RequestHandler):
  """Renders customers summary."""
  def get(self):
    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/customers.html')
    self.response.out.write(template.render(path, {'config': config.Config}))


class CustomerView(webapp.RequestHandler):
  """Renders summary for one customer."""
  def GetTemplateValues(self):
    id = self.request.get('id')
    customer = model.Customer.get_by_key_name(id)
    return {'customer': customer,
            'config': config.Config}

  def get(self):
    template_values = self.GetTemplateValues()

    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/customer.html')
    self.response.out.write(template.render(path, template_values))
