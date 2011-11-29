#!/usr/bin/env python
# encoding: utf-8
"""
expenses.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""
import collections
import logging
import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from util import product_util
from util import region_util
import model


EXPENSES_LIMIT = 20


class ExpensesView(webapp.RequestHandler):
  def get(self):
    """Renders JSON for pie chart.
    """
    query = model.Expense.all()

    dim = self.request.get('dim')
    if dim != 'supplier':
      if self.request.get('supplier'):
        query.filter('supplier =  ', db.Key.from_path('Supplier', self.request.get('supplier')))
      else:
        query.filter('supplier =  ', model.Supplier.Aggregated())

    if dim != 'customer':
      if self.request.get('customer'):
        query.filter('customer =  ', db.Key.from_path('Customer', self.request.get('customer')))
      else:
        query.filter('customer =  ', model.Customer.Aggregated())

    if dim != 'region':
      if not self.request.get('region'):
        query.filter('region = ', model.AGGREGATE_REGION)
      else:
        query.filter('region = ', self.request.get('region'))

    if dim != 'type':
      if not self.request.get('type'):
        query.filter('type = ', model.AGGREGATE_TYPE)
      else:
        query.filter('type = ', self.request.get('type'))

    query.filter('date = ', model.AGGREGATE_DATE).order('-amount')

    self.response.headers['Content-Type'] = 'application/json;charset=utf-8'

    if dim == 'type':
      path = os.path.join(os.path.dirname(__file__), '../templates/types.json')
      self.response.out.write(
          template.render(path, {'records':
                                 [{'category': product_util.ProductCategory.NameByCode(record.type),
                                   'value': record.amount}
                                  for record in query
                                  if record.type != model.AGGREGATE_TYPE]}))
    elif dim == 'region':
      region_values = [{'key': record.region,
                        'name': region_util.names[record.region],
                        'value': record.amount}
                       for record in query
                       if record.region != model.AGGREGATE_REGION]
      path = os.path.join(os.path.dirname(__file__), '../templates/regions.json')
      self.response.out.write(template.render(path,
                                              {'records': region_values}))
    elif dim == 'supplier':
      supplier_data = collections.defaultdict(lambda: 0.0)

      template_values = {'records':
              [{'supplier': record.supplier, 'value': record.amount}
               for record in query.fetch(EXPENSES_LIMIT + 1)
               if model.Expense.supplier.get_value_for_datastore(record) != model.Supplier.Aggregated().key()]
             }
      path = os.path.join(os.path.dirname(__file__), '../templates/suppliers.json')
      self.response.out.write(template.render(path, template_values))
    elif dim == 'customer':
      customer_data = collections.defaultdict(lambda: 0.0)
      template_values = {'records':
              [{'customer': record.customer, 'value': record.amount}
               for record in query.fetch(EXPENSES_LIMIT + 1)
               if model.Expense.customer.get_value_for_datastore(record) != model.Customer.Aggregated().key()]
             }
      path = os.path.join(os.path.dirname(__file__), '../templates/customers.json')
      self.response.out.write(template.render(path, template_values))
