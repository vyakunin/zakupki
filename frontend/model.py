#!/usr/bin/python2.5
# encoding: utf-8
"""
app.py

Copyright (c) Sergey Babenko and Vladimir Yakunin 2011.
All rights reserved.
"""

from google.appengine.api import datastore
from google.appengine.ext import db

class Customer(db.Model):
  reg_num = db.StringProperty(required=True)
  full_name = db.TextProperty(required=True)
  inn = db.StringProperty(required=True)
  kpp = db.StringProperty(required=True)
  tofk = db.StringProperty(required=True)

  @classmethod
  def Aggregated(cls):
    """Returns special Customer used for aggregation"""
    return cls.get_or_insert('0',
                             reg_num='0',
                             full_name='Aggregated',
                             inn='0',
                             kpp='0',
                             tofk='0')

  
class Supplier(db.Model):
  participant_type = db.StringProperty()
  inn = db.StringProperty(required=True)
  kpp = db.StringProperty(required=True)
  organization_form = db.StringProperty()
  organization_name = db.TextProperty(required=True)
  factual_address = db.StringProperty()
  
  @classmethod
  def Aggregated(cls):
    """Returns special Supplier used for aggregation"""
    return cls.get_or_insert('0',
                             inn='0',
                             kpp='0',
                             organization_name='Aggregated')

class Expense(db.Model):
  # Who pays
  customer = db.ReferenceProperty(Customer, required=True)
  # Who recieves money
  supplier = db.ReferenceProperty(Supplier, required=True)
  # How much money
  amount = db.FloatProperty(required=True)
  # In what date they do pay
  date = db.DateProperty(required=True)
  # Region of payment
  region = db.StringProperty(required=True)  # 2-digit code
