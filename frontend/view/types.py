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


class ByTypeView(webapp.RequestHandler):
  def get(self):
    """Renders JSON for pie chart.
    """

    query = (model.Expense.all()
        .filter('supplier =  ', model.Supplier.Aggregated())
        .filter('customer = ', model.Customer.Aggregated())
        .filter('date = ', model.AGGREGATE_DATE)
        .order('-amount'))

    region = self.request.get('code')
    if not region:
      logging.info("Hello world")
      query = query.filter('region = ', model.AGGREGATE_REGION)
    else:
      query = query.filter('region = ', region)

    self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/region_pie_chart.json')
    self.response.out.write(
        template.render(path, {'records':
                               [{'category': product_util.ProductCategory.ByCode(str(record.type)),
                                 'value': record.amount}
                                for record in query
                                if record.type != model.AGGREGATE_TYPE]}))
