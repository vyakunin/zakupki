#!/usr/bin/env python
# encoding: utf-8
"""
by_region.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""

import collections
import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import model

TEMPLATE_PATH = '../templates/region.json'


class ByRegionView(webapp.RequestHandler):
  def get(self):
    """Implements GET request handler.

    Parameters:
      none:
    """    
    query = (model.Expense.all()
      .filter('supplier = ', model.Supplier.Aggregated())
      .filter('customer = ', model.Customer.Aggregated()))
    
    values_dict = collections.defaultdict(lambda: 0.0)
    for record in query:
      values_dict[record.region] += record.amount
    
    region_values = [{'region': r, 'value': v}
                     for r, v in sorted(values_dict.items(),
                                        key=lambda a:a[1],
                                        reverse=True)]

    self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), TEMPLATE_PATH)
    self.response.out.write(template.render(path, {'records': region_values}))
