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
from view import expenses
from view import regions
from view import suppliers
from view import time_chart


app = webapp2.WSGIApplication(
    [('/', homepage.HomePageView),
     ('/regions', regions.RegionsView),
     ('/region', regions.RegionView),
     ('/time_chart', time_chart.TimeChartView),
     ('/customer', customers.CustomerView),
     ('/supplier', suppliers.SupplierView),
     ('/expenses', expenses.ExpensesView),
    ],
    debug=True)
