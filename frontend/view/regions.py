#!/usr/bin/env python
# encoding: utf-8
"""
regions.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""

import collections
import datetime
import logging
import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import model


TEMPLATE_PATH = '../templates/region_table.json'
# date format for requests
DATE_FORMAT = '%Y.%m.%d'

def get_dates(request):
 return map(parse_date, 
              (request.get('date_from'),
               request.get('date_to')))


def parse_date(date):
  if date:
    return datetime.strptime(date, DATE_FORMAT)
  else:
    return None


class RegionView(webapp.RequestHandler):
  """Render view for one selected region."""
  
  def GetTemplateValues(self):
    return {'region_name': "Москва (заглушка)",
            'region_code': self.request.get('code')}
  
  def get(self):
    region = self.request.get('code')
    if not region:
      self.response.set_status(404)
      return
    
    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/region.html')
    self.response.out.write(template.render(path, 
                                            self.GetTemplateValues()))
    

class ByRegionView(webapp.RequestHandler):
  def get(self):
    """Renders JSON data for regions table.

    Parameters:
      none:
    """    
    date_from, date_to = get_dates(self.request) 

    query = (model.Expense.all()
        .filter('supplier = ', model.Supplier.Aggregated())
        .filter('customer = ', model.Customer.Aggregated())
        .filter('type = ', model.AGGREGATE_TYPE))
    if date_from and date_to:
      query = (query.filter('date > ', date_from)
          .filter('date < ', date_to))
    else:
      query = query.filter('date = ', model.AGGREGATE_DATE)

    values_dict = collections.defaultdict(lambda: 0.0)
    for record in query:
      if record.region != model.AGGREGATE_REGION:
        values_dict[record.region] += record.amount
    
    region_values = [{'key': r, 'value': v}
                     for r, v in sorted(values_dict.items(),
                                        key=lambda a:a[1],
                                        reverse=True)]
    self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), TEMPLATE_PATH)
    logging.info(region_values)
    self.response.out.write(template.render(path,
                                            {'records': region_values}))


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


class ByMonthView(webapp.RequestHandler):
  def get(self):
    """Renders JSON for bar chart
    """
    region = self.request.get('code')
    if not region:
      self.response.set_status(404, 'Wrong region code')
      return
    
    query = (model.Expense.all()
      .filter('region = ', region)
      .filter('supplier =  ', model.Supplier.Aggregated())
      .filter('customer = ', model.Customer.Aggregated())
      .filter('type = ', model.AGGREGATE_TYPE)
      .order('date'))

    values_dict = collections.defaultdict(lambda: 0.0)
    template_records = []
    last_date = None
    for record in query:
      if record.date >= model.AGGREGATE_DATE.date():
        continue

      logging.info(record.date)

      if not last_date:
        last_date = record.date
        value = record.amount
      else:
        while not IsPreviousMonth(record.date, last_date):
          last_date = GetNextMonth(last_date)
          template_records.append({'month' :last_date.strftime('%b %y'),
                                   'value': 0.0})

        last_date = record.date
        value = record.amount
        
      template_records.append({'month' :last_date.strftime('%b %y'),
                               'value': value})

    self.response.headers['Content-Type'] = 'application/json;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/region_bar_chart.json')
    self.response.out.write(template.render(path,
                                            {'records': template_records}))


