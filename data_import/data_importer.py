#!/usr/bin/python2.5
# encoding: utf-8
"""
app.py

Copyright (c) Sergey Babenko and Vladimir Yakunin 2011.
All rights reserved.
"""

from lxml import etree

class XmlImporter(object):
  """Provides iterator over tuples of strings given xml."""


  data = None
  
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

  @staticmethod
  def ParseData(data):
    """Parses contract.xml in zakupki.gov format

    Args:
      data: File-like object with XML.

    Returns:
      {dict} {spents:[(date, sum, customer, contractor, region)],
              customers:[(regNum, fullName, inn, kpp, tofk)],
              suppliers:[(participantType, inn, kpp, organizationForm,
                          organizationName, factualAdress)]}.
    """
    tree = etree.parse(data)
    namespaces = {'oos' : 'http://zakupki.gov.ru/oos/types/1'}
    for record in tree.xpath('/contract', namespaces=namespaces):
      date = record.xpath('string(./oos:protocolDate)', namespaces=namespaces)
      amount = record.xpath('string(./oos:price)', namespaces=namespaces)
      currencyCode = record.xpath('string(./oos:currency/oos:code)', namespaces=namespaces)
      assert currencyCode==RUB
      customer = ParseCustomer(record.xpath('./oos:customer)', namespaces=namespaces), namespaces)
      AddCustomer(customer)
      supplierCount = 0
      for supplierRecord in record.xpath('./oos:suppliers', namespaces=namespaces):
        supplier = ParseSupplier(supplierRecord)
        ++supplierCount
      assert supplierCount < 2 #TODO(vyakunin): can't understand what I do if its false
      
          

  @classmethod
  def AddCustomer(customer):
    """Adds customer to dictionary if was absent."""
    if not customer['regNum'] in customers:
      customers[customer['regNum']] = customer 

  @classmethod
  def AddSupplier(supplier):
    """Adds supplier to dictionary if was absent."""
    if not supplier['inn'] in suppliers: #  TODO(vyakunin): is it correct to use inn as key?
      suppliers[supplier['inn']] = supplier 
      
