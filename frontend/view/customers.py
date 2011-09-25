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

HTML_TEMPLATE_PATH = '../templates/customers.html'
JSON_TEMPLATE_PATH = '../templates/customers.json'
DATE_FORMAT = '%Y.%m.%d'


class TopCustomerView(webapp.RequestHandler):
  def GetTemplateValues(self):
    start_date_str = self.request.get('start_date')
    end_date_str = self.request.get('end_date')

    query = (model.Expense.all()
        .filter('supplier = ', model.Supplier.Aggregated()))
    
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

    query = query.order('-amount')    
    query = query.fetch(int(self.request.get('limit', '20')))

    customer_data = collections.defaultdict(lambda: 0.0)
    for expense in query:
      customer_key = model.Expense.customer.get_value_for_datastore(expense).name()
      if customer_key != model.Customer.Aggregated().key().name():
        customer_data[customer_key] += expense.amount

    logging.info(customer_data.keys())
    logging.info(model.Customer.get_by_key_name(customer_data.keys()))
    logging.info([(c.key(), c)
                  for c in model.Customer.get_by_key_name(customer_data.keys())])

    customers_dict = dict((c.key().name(), c)
                          for c in model.Customer.get_by_key_name(customer_data.keys()))

    return {'records':
            [{'customer': customers_dict[key], 'value': value}
             for key, value in sorted(customer_data.items(),
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

    if view_type == 'html':
      self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
      path = os.path.join(os.path.dirname(__file__), HTML_TEMPLATE_PATH)
      self.response.out.write(template.render(path, template_values))
    elif view_type == 'json':
      self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
      path = os.path.join(os.path.dirname(__file__), JSON_TEMPLATE_PATH)
      self.response.out.write(template.render(path, template_values))
