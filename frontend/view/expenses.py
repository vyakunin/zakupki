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

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from util import product_util
from util import region_util
import model

_MEMCACHE_TIMEOUT = 60*60*12  # 12 hours
EXPENSES_LIMIT = 20

def BuildMemcacheKey(request):
  dim = request.get('dim')
  request_description = 'dim: ' + dim  
  # we build key 'param1: v1, param2: v2' and so on.
  # We are not escaping values yet, should think about it.
  request_parameters = ['supplier', 'customer', 'region', 'type']
  for param in request_parameters:
    value = request.get(param)
    if (value):
      request_description.append(
        ', %s: %s' % (param, value))
  return request_description

def BuildPathAndTemplateValues(request):
  query = model.Expense.all()

  dim = request.get('dim')
  if dim != 'supplier':
    if request.get('supplier'):
      query.filter('supplier =  ', db.Key.from_path('Supplier', request.get('supplier')))
    else:
      query.filter('supplier =  ', model.Supplier.Aggregated())

  if dim != 'customer':
    if request.get('customer'):
      query.filter('customer =  ', db.Key.from_path('Customer', request.get('customer')))
    else:
      query.filter('customer =  ', model.Customer.Aggregated())

  if dim != 'region':
    if not request.get('region'):
      query.filter('region = ', model.AGGREGATE_REGION)
    else:
      query.filter('region = ', request.get('region'))

  if dim != 'type':
    if not request.get('type'):
      query.filter('type = ', model.AGGREGATE_TYPE)
    else:
      query.filter('type = ', request.get('type'))

  query.filter('date = ', model.AGGREGATE_DATE).order('-amount')

  if dim == 'type':
    path = os.path.join(os.path.dirname(__file__), '../templates/types.json')
    return (path, {'records':
                   [{'category': product_util.ProductCategory.NameByCode(record.type),
                     'value': record.amount}
                    for record in query
                    if record.type != model.AGGREGATE_TYPE]})
  elif dim == 'region':
    region_values = [{'key': record.region,
                      'name': region_util.names[record.region],
                      'value': record.amount}
                     for record in query
                     if record.region != model.AGGREGATE_REGION]
    path = os.path.join(os.path.dirname(__file__), '../templates/regions.json')
    return (path, {'records': region_values})
  elif dim == 'supplier':
    supplier_data = collections.defaultdict(lambda: 0.0)

    template_values = {'records':
            [{'supplier': record.supplier, 'value': record.amount}
             for record in query.fetch(EXPENSES_LIMIT + 1)
             if model.Expense.supplier.get_value_for_datastore(record) != model.Supplier.Aggregated().key()]
           }
    path = os.path.join(os.path.dirname(__file__), '../templates/suppliers.json')
    return (path, template_values)
  elif dim == 'customer':
    customer_data = collections.defaultdict(lambda: 0.0)
    template_values = {'records':
            [{'customer': record.customer, 'value': record.amount}
             for record in query.fetch(EXPENSES_LIMIT + 1)
             if model.Expense.customer.get_value_for_datastore(record) != model.Customer.Aggregated().key()]
           }
    path = os.path.join(os.path.dirname(__file__), '../templates/customers.json')
    return (path, template_values)

def FindOrBuildPathAndTemplateValues(request):
  memcache_key = BuildMemcacheKey(request)
  path_and_template_values = memcache.get(memcache_key)
  if path_and_template_values is not None:
    return path_and_template_values
  path_and_template_values = BuildPathAndTemplateValues(request)
  memcache.set(memcache_key, path_and_template_values, _MEMCACHE_TIMEOUT)
  return path_and_template_values

class ExpensesView(webapp.RequestHandler):
  def get(self):
    """Renders JSON for pie chart.
    """
    (path, template_values) = FindOrBuildPathAndTemplateValues(self.request)
    
    self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
    self.response.out.write(template.render(path, template_values))
    

