#!/usr/bin/env python
# encoding: utf-8
"""
regions.py

Copyright (c) 2011 All its authors.
All rights reserved.
"""

import collections
import logging
import os

from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import model


TEMPLATE_PATH = '../templates/region.json'
# date format for requests
DATE_FORMAT = '%Y.%m.%d'

class RegionView(webapp.RequestHandler):
  """Render view for one selected region."""
  
  def GetTemplateValues(self):
    return {'region_name': "Москва (заглушка)",
            'region_code': self.request.get('code')}
  
  def get(self):
    region = self.request.get('code')
    logging.info(region)
    if not region:
      self.response.set_status(404)
      return
    
    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), '../templates/region_view.html')
    self.response.out.write(template.render(path, 
                                            self.GetTemplateValues()))
    

class ByRegionView(webapp.RequestHandler):
  def get(self):
    """Implements GET request handler.

    Parameters:
      none:
    """    
    date_from, date_to = get_dates(self.request) 

    query = (model.Expense.all()
        .filter('supplier = ', model.Supplier.Aggregated())
        .filter('customer = ', model.Customer.Aggregated()))
    if date_from and date_to:
      query = (query.filter('date > ', date_from)
          .filter('date < ', date_to))
    else:
      query = query.filter('date = ', model.AGGREGATE_DATE)

    values_dict = collections.defaultdict(lambda: 0.0)
    for record in query:
      values_dict[record.region] += record.amount
    
    region_values = [{'key': r, 'value': v}
                     for r, v in sorted(values_dict.items(),
                                        key=lambda a:a[1],
                                        reverse=True)]
    columns = [{'id': 'region', 'label': 'Регион', 'type': 'string'},
               {'id': 'sum', 'label': 'Сумма', 'type': 'number'}]

    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), TEMPLATE_PATH)
    self.response.out.write(template.render(path, {
                                                   'records': region_values,
                                                   'columns': columns}))

def get_dates(request):
 return map(parse_date, 
              (request.get('date_from'),
               request.get('date_to')))

def parse_date(date):
  if date:
    return datetime.strptime(date, DATE_FORMAT)
  else:
    return None

class ByMonthView(webapp.RequestHandler):
  """Gets month - sum data per region
  """
  def get(self):
    date_from, date_to = get_dates(self.request)
    region = self.request.get('region_id', '08')
    
    values_dict = collections.defaultdict(lambda: 0.0)
    query = (model.Expense.all()
      .filter('region = ', region)
      .filter('date > ', date_from)
      .filter('date < ', date_to))

    for record in query:
      values_dict[record.date] += record.amount

    region_values = [{'key': r, 'value': v}
                     for r, v in sorted(values_dict.items(),
                                        key=lambda a:a[1],
                                        reverse=True)]
    columns = [{'id': 'month', 'label': 'Месяц', 'type': 'string'},
               {'id': 'sum', 'label': 'Сумма', 'type': 'number'}]

    self.response.headers['Content-Type'] = 'text/html;charset=utf-8'
    path = os.path.join(os.path.dirname(__file__), TEMPLATE_PATH)
    self.response.out.write(template.render(path, {
                                                   'records': region_values,
                                                   'columns': columns}))


