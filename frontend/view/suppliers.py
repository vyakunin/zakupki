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

HTML_TEMPLATE_PATH = '../templates/suppliers.html'
JSON_TEMPLATE_PATH = '../templates/suppliers.json'
DATE_FORMAT = '%Y.%m.%d'


class TopSuppliersView(webapp.RequestHandler):
  def GetTemplateValues(self):
    start_date_str = self.request.get('start_date')
    end_date_str = self.request.get('end_date')

    query = (model.Expense.all()
        .filter('customer = ', model.Customer.Aggregated())
        .filter('type = ', model.AGGREGATE_TYPE))
    
    if start_date_str and end_date_str:
      start_date = datetime.datetime.strptime(start_date_str, DATE_FORMAT)
      end_date = datetime.datetime.strptime(end_date_str, DATE_FORMAT)
      query = (query
          .filter('date >=', start_date)
          .filter('date <=', end_date))
    else:
      query = query.filter('date = ', model.AGGREGATE_DATE)

    if self.request.get('region'):
      query = query.filter('region = ', self.request.get('region'))
    else:
      query = query.filter('region = ', model.AGGREGATE_REGION)
  
    query = query.order('-amount')
    query = query.fetch(int(self.request.get('limit', '20')))

    supplier_data = collections.defaultdict(lambda: 0.0)
    for expense in query:
      supplier_key = model.Expense.supplier.get_value_for_datastore(expense).name()
      if supplier_key != model.Supplier.Aggregated().key().name():
        supplier_data[supplier_key] += expense.amount

    suppliers_dict = dict((c.key().name(), c)
                          for c in model.Supplier.get_by_key_name(supplier_data.keys()))

    return {'records':
            [{'supplier': suppliers_dict[key], 'value': value}
             for key, value in sorted(supplier_data.items(),
                                      key=lambda a:a[1],
                                      reverse=True)]
           }

  def get(self):
    """Generates output

    Parameters:
      start_date: date in format 'YYYY.MM.DD'
      end_date: date in format 'YYYY.MM.DD'
      region: Optional 2-digit region code
      view: ['json','html'], default is 'html'
    """
    view_type = self.request.get('view', 'html')
    template_values = self.GetTemplateValues()
    logging.info(template_values)

    if view_type == 'html':
      self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
      path = os.path.join(os.path.dirname(__file__), HTML_TEMPLATE_PATH)
      self.response.out.write(template.render(path, template_values))
    elif view_type == 'json':
      self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
      path = os.path.join(os.path.dirname(__file__), JSON_TEMPLATE_PATH)
      self.response.out.write(template.render(path, template_values))
