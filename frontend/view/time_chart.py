#!/usr/bin/env python
# encoding: utf-8
"""
time_chart.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""

import collections
import datetime
import json
import logging
import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import model

def IsPreviousMonth(test_date, last_date):
  """Returns true of last_date is the same day of the previous month for test_date"""
  return (test_date.day == last_date.day and
          (test_date.month - last_date.month == 1 or
           test_date.month == 1 and last_date.month == 12))


def GetNextMonth(date):
  """Returns the same day of the next month"""
  if date.month == 12:
    return datetime.date(date.year +1, 1, date.day)
  else:
    return datetime.date(date.year, date.month +1, date.day)


MONTHS = {
   1: 'Январь',
   2: 'Февраль',
   3: 'Март',
   4: 'Апрель',
   5: 'Май',
   6: 'Июнь',
   7: 'Июль',
   8: 'Август',
   9: 'Сентябрь',
   10: 'Октябрь',
   11: 'Ноябрь',
   12: 'Декабрь',
}

class TimeChartView(webapp.RequestHandler):
  def get(self):
    """Renders JSON for bar chart
    """
    query = model.Expense.all()

    if self.request.get('supplier'):
      query.filter('supplier = ', db.Key.from_path('Supplier', self.request.get('supplier')))
    else:
      query.filter('supplier =  ', model.Supplier.Aggregated())

    if self.request.get('customer'):
      query.filter('customer = ', db.Key.from_path('Customer', self.request.get('customer')))
    else:
      query.filter('customer =  ', model.Customer.Aggregated())

    if self.request.get('type'):
      query.filter('type = ', self.request.get('type'))
    else:
      query.filter('type = ', model.AGGREGATE_TYPE)

    if self.request.get('region'):
      query.filter('region = ', self.request.get('region'))
    else:
      query.filter('region = ', model.AGGREGATE_REGION)

    query.order('date')

    values_dict = collections.defaultdict(lambda: 0.0)
    template_records = []
    last_date = None
    for record in query:
      if (record.date >= model.AGGREGATE_DATE.date() or
          record.date.month == 12 and record.date.day == 31):
        continue

      if not last_date:
        last_date = record.date
        value = record.amount
      else:
        while not IsPreviousMonth(record.date, last_date):
          last_date = GetNextMonth(last_date)
          template_records.append({'month': '%s %s' % (MONTHS[last_date.month], last_date.year),
                                   'value': 0.0})

        last_date = record.date
        value = record.amount

      template_records.append({'month': '%s %s' % (MONTHS[last_date.month], last_date.year),
                               'value': value})

    self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
    json.dump(
        {'cols': [{'id': 'month', 'label': 'Месяц', 'type': 'string'},
                  {'id': 'sum', 'label': 'Сумма', 'type': 'number'}],
         'rows': [{'c': [{'v': r['month']}, {'v': r['value']}]}
                  for r in template_records]
        },
        self.response.out,
        ensure_ascii=False)
