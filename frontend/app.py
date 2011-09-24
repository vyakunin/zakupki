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
from view import customers
from view import regions

application = webapp.WSGIApplication(
    [('/regions.json', regions.ByRegionView),
     ('/top_customers', customers.TopCustomerView),
    ],
    debug=True)


def main():
  logging.getLogger().setLevel(logging.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
