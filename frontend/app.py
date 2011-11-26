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
from view import types


app = webapp2.WSGIApplication(
    [('/', homepage.HomePageView),
     ('/region', regions.RegionView),
     ('/regions.json', regions.ByRegionView),
     ('/region_bar_chart.json', regions.ByMonthView),
     ('/region_pie_chart.json', types.ByTypeView),
     ('/top_customers', customers.TopCustomerView),
     ('/top_suppliers', suppliers.TopSuppliersView),
    ],
    debug=True)
