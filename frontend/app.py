#!/usr/bin/python2.5
# encoding: utf-8
"""
app.py

Copyright (c) its authors.
All rights reserved.
"""

import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from view import homepage
from view import customers
from view import regions
from view import suppliers
from view import types


application = webapp.WSGIApplication(
    [('/', homepage.HomePageView),
     ('/region', regions.RegionView),
     ('/regions.json', regions.ByRegionView),
     ('/region_bar_chart.json', regions.ByMonthView),
     ('/region_pie_chart.json', types.ByTypeView),
     ('/top_customers', customers.TopCustomerView),
     ('/top_suppliers', suppliers.TopSuppliersView),
    ],
    debug=True)


def main():
  logging.getLogger().setLevel(logging.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
