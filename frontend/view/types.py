#!/usr/bin/env python
# encoding: utf-8
"""
type.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""
import logging
import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from util import product_util
import model


class TypesChartView(webapp.RequestHandler):
  def get(self):
    """Renders JSON for pie chart.
    """
    query = model.Expense.all()
    if self.request.get('supplier'):
      query = query.filter('supplier =  ', db.Key.from_path('Supplier', self.request.get('supplier')))
    else:
      query = query.filter('supplier =  ', model.Supplier.Aggregated())

    if self.request.get('customer'):
      logging.info('Filter by customer')
      query = query.filter('customer =  ', db.Key.from_path('Customer', self.request.get('customer')))
    else:
      query = query.filter('customer =  ', model.Customer.Aggregated())

    if not self.request.get('code'):
      query = query.filter('region = ', model.AGGREGATE_REGION)
    else:
      query = query.filter('region = ', self.request.get('code'))

    query = query.filter('date = ', model.AGGREGATE_DATE).order('-amount')
    
    self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/types.json')
    self.response.out.write(
        template.render(path, {'records':
                               [{'category': product_util.ProductCategory.NameByCode(record.type),
                                 'value': record.amount}
                                for record in query
                                if record.type != model.AGGREGATE_TYPE]}))
