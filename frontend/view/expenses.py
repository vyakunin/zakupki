#!/usr/bin/env python
# encoding: utf-8
"""
expenses.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""
import collections
import json
import logging
import os
import StringIO

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from util import product_util
from util import region_util
import model

_MEMCACHE_TIMEOUT = 60*60*12  # 12 hours
EXPENSES_LIMIT = 20

# Maps dimension to relative table column label.
DIM_TO_LABEL = {
    'supplier': 'Поставщик',
    'customer': 'Покупатель',
    'region': 'Регион',
    'type': 'Категория'
}

def SupplierTitle(record):
  key = model.Expense.supplier.get_value_for_datastore(record)
  future = db.get_async(key)
  def AsyncResult():
    return '<a href="/supplier?id=%s">%s</a>' % (
        key.name(), future.get_result().organization_name)
  return AsyncResult

def CustomerTitle(record):
  key = model.Expense.customer.get_value_for_datastore(record)
  future = db.get_async(key)
  def AsyncResult():
    return '<a href="/customer?id=%s">%s</a>' % (
        key.name(), future.get_result().full_name)
  return AsyncResult

def RegionTitle(record):
  return lambda: '<a href="/region?code=%s">%s</a>' % (
      record.region, region_util.names.get(record.region, '??'))

def TypeTitle(record):
  return lambda: product_util.ProductCategory.NameByCode(record.type)

# Callables returning row's name by a record.
RECORD_TO_TITLE = {
    'supplier': SupplierTitle,
    'customer': CustomerTitle,
    'region': RegionTitle,
    'type': TypeTitle
}
# Maps property to their relative aggregated value.
DIM_TO_AGGREGATED_VALUE = {
    'supplier': model.Supplier.Aggregated().key(),
    'customer': model.Customer.Aggregated().key(),
    'region': model.AGGREGATE_REGION,
    'type': model.AGGREGATE_TYPE
}


def BuildResult(request):
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

  if dim in ['supplier', 'customer']:
    query = query.fetch(EXPENSES_LIMIT)

  async_records = [(RECORD_TO_TITLE[dim](r), r.amount)
                   for r in query
                   if model.Expense.properties()[dim].get_value_for_datastore(r) != DIM_TO_AGGREGATED_VALUE[dim]]
  return json.dumps(
      {'cols': [{'id': dim, 'label': DIM_TO_LABEL[dim], 'type': 'string'},
                {'id': 'sum', 'label': 'Сумма', 'type': 'number'}],
       'rows': [{'c': [{'v': rec[0]()},
                       {'v': rec[1]}]}
                for rec in async_records]})


def BuildMemcacheKey(request):
  dim = request.get('dim')
  request_description = 'dim: ' + dim
  # we build key 'param1: v1, param2: v2' and so on.
  # We are not escaping values yet, should think about it.
  request_parameters = ['supplier', 'customer', 'region', 'type']
  for param in request_parameters:
    value = request.get(param)
    if (value):
      request_description += ', %s: %s' % (param, value)

  return request_description


def FindOrBuildResult(request):
  memcache_key = BuildMemcacheKey(request)
  path_and_template_values = memcache.get(memcache_key)
  if path_and_template_values is not None:
    return path_and_template_values
  path_and_template_values = BuildResult(request)
  memcache.set(memcache_key, path_and_template_values, _MEMCACHE_TIMEOUT)
  return path_and_template_values


class ExpensesView(webapp.RequestHandler):
  def get(self):
    """Renders JSON for different charts.
    """
    result = FindOrBuildResult(self.request)

    self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
    self.response.out.write(result)
