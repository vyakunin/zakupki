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

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from util import product_util
from util import region_util
import model


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

    if dim in ['supplier', 'customer']:
      query = query.fetch(EXPENSES_LIMIT)

    self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
    async_records = [(RECORD_TO_TITLE[dim](r), r.amount)
                     for r in query
                     if model.Expense.properties()[dim].get_value_for_datastore(r) != DIM_TO_AGGREGATED_VALUE[dim]]
    json.dump(
        {'cols': [{'id': dim, 'label': DIM_TO_LABEL[dim], 'type': 'string'},
                  {'id': 'sum', 'label': 'Сумма', 'type': 'number'}],
         'rows': [{'c': [{'v': rec[0]()},
                         {'v': rec[1]}]}
                  for rec in async_records]},
        self.response.out,
        ensure_ascii=False)
