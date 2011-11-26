#!/usr/bin/python2.7
# encoding: utf-8
"""
app.py

Copyright (c) its authors.
All rights reserved.
"""

import webapp2

from view import homepage
from view import customers
from view import regions
from view import suppliers
from view import time_chart
from view import types


app = webapp2.WSGIApplication(
    [('/', homepage.HomePageView),
     ('/region', regions.RegionView),
     ('/regions.json', regions.ByRegionView),
     ('/time_chart.json', time_chart.TimeChartView),
     ('/types.json', types.TypesChartView),
     ('/customer', customers.CustomerView),
     ('/top_customers', customers.TopCustomerView),
     ('/top_suppliers', suppliers.TopSuppliersView),
    ],
    debug=True)
