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
from view import time_chart


app = webapp2.WSGIApplication(
    [('/', homepage.HomePageView),
     ('/region', regions.RegionView),
     ('/time_chart.json', time_chart.TimeChartView),
     ('/customer', customers.CustomerView),
     ('/expenses', expenses.ExpensesView),
    ],
    debug=True)
