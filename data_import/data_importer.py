#!/usr/bin/python2.5
# encoding: utf-8
"""
app.py

Copyright (c) Sergey Babenko and Vladimir Yakunin 2011.
All rights reserved.
"""

from lxml import etree
import csv

class XmlImporter(object):
  """Provides iterator over tuples of strings given xml."""

  @staticmethod
  def ParseCustomer(customer, namespaces):
    """Parses customer data from xml subtree"""
    regNum = customer.xpath('string(oos:regNum)', namespaces)
    fullName = customer.xpath('string(oos:fullName)', namespaces)
    inn = customer.xpath('string(oos:inn)', namespaces)
    kpp = customer.xpath('string(oos:kpp)', namespaces)
    return {'regNum':regNum, 'fullName':fullName, 'inn':inn, 'kpp':kpp}

  @staticmethod
  def ParseSupplier(supplier, namespaces):
    """Parses supplier data from xml subtree"""
    participantType = supplier.xpath('string(oos:participantType)', namespaces)
    inn = supplier.xpath('string(oos:inn)', namespaces)
    kpp = supplier.xpath('string(oos:kpp)', namespaces)
    organizationForm = supplier.xpath('string(oos:organizationForm)', namespaces)
    organizationName = supplier.xpath('string(oos:organizationName)', namespaces)
    factualAdress = supplier.xpath('string(oos:factualAdress)', namespaces)
    return {'participantType':participantType,
            'inn':inn,
            'kpp':kpp,
            'organizationForm':organizationForm,
            'organizationName':organizationName,
            'factualAdress':factualAdress}

  def ParseData(self, data):
    """Parses contract.xml in zakupki.gov format

    Args:
      data: File-like object with XML.

    Returns:
      {dict} {spents:[(date, sum, customer, supplier, region)],
              customers:[{regNum, fullName, inn, kpp, tofk}],
              suppliers:[{participantType, inn, kpp, organizationForm,
                          organizationName, factualAdress}]}.
    """
    self.suppliers = {}
    self.customers = {}
    spents = []
    tree = etree.parse(data)
    namespaces = {'oos' : 'http://zakupki.gov.ru/oos/types/1'}
    for record in tree.xpath('/contract', namespaces=namespaces):
      date = record.xpath('string(./oos:protocolDate)', namespaces=namespaces)
      date = date[:-2] + '01'
      amount = record.xpath('float(./oos:price)', namespaces=namespaces)
      currencyCode = record.xpath('string(./oos:currency/oos:code)', namespaces=namespaces)
      assert currencyCode==RUB
      customer = ParseCustomer(record.xpath('./oos:customer)', namespaces=namespaces), namespaces)
      AddCustomer(customer)
      supplierCount = 0
      for supplierRecord in record.xpath('./oos:suppliers', namespaces=namespaces):
        supplier = ParseSupplier(supplierRecord)
        ++supplierCount
      assert supplierCount < 2 #TODO(vyakunin): can't understand what I do if its false
      AddSupplier(supplier)
      spents.append((date, 
                     sum,
                     customer['regNum'],
                     contractor['inn'],
                     customer['inn'][:2]))
    return {'spents': spents,
            'suppliers': self.suppliers.values(),
            'customers': self.customers.values()}

  @staticmethod
  def PrintSpents(spents, filename, aggregate_customer, aggregate_supplier, aggregate_region):
    csvWriter = csv.writer(open(filename, 'wb'), delimiter=',',
                           quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamWriter.writerow(['date', 'sum', 'customer', 'contractor', 'region'])
    aggregatedSpents = {}
    for spent in spents:
      key = [spent[0]]
      if aggregate_customer: #  TODO(vyakunin): palevo
        key.append('*')
      else:
        key.append(spent[2])
      if aggregate_supplier:
        key.append('*')
      else:
        key.append(spent[3])
      if aggregate_region:
        key.append('*')
      else:
        key.append(spent[4])
      key = tuple(key)
      aggregatedSpents[key] += spent[1]
    for key, value in aggregatedSpents.iteritems():
      csvWriter.writerow([key[0], value].extend(list(key[1:])))
    
#customers:[{regNum, fullName, inn, kpp, tofk}],
 #             suppliers:[{participantType, inn, kpp, organizationForm,
  #                        organizationName, factualAdress}]}.
  @staticmethod
  def PrintCustomers(customers, filename):
    csvWriter = csv.DictWriter(open(filename, 'wb'),
                               ['regNum', 'fullName', 'inn',
                                'kpp', 'tofk'],
                               delimiter=',',
                               quotechar='"',
                               quoting=csv.QUOTE_MINIMAL)
    for customer in customers:
      csvWriter.writerow(customer)
    
  @staticmethod
  def PrintSuppliers(suppliers, filename):
    csvWriter = csv.DictWriter(open(filename, 'wb'),
                               ['participantType', 'inn'
                                'kpp', 'organizationForm',
                                'organizationName', 'factualAdress'],
                               delimiter=',',
                               quotechar='"',
                               quoting=csv.QUOTE_MINIMAL)
    for supplier in suppliers:
      csvWriter.writerow(supplier)
    
  def AddCustomer(self, customer):
    """Adds customer to dictionary if was absent."""
    if not customer['regNum'] in self.customers:
      self.customers[customer['regNum']] = customer 

  def AddSupplier(self, supplier):
    """Adds supplier to dictionary if was absent."""
    if not supplier['inn'] in self.suppliers: #  TODO(vyakunin): is it correct to use inn as key?
      self.suppliers[supplier['inn']] = supplier


      
