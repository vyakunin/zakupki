#!/usr/bin/python2.6
# encoding: utf-8
"""
data_importer.py

Copyright (c) Sergey Babenko and Vladimir Yakunin 2011.
All rights reserved.
"""

from lxml import etree

import csv
import getopt
import math
import os
import sys
import dateutil.parser
import zipfile

class XmlImporter(object):
  """Provides iterator over tuples of strings given xml."""

  namespaces = {'oos' : 'http://zakupki.gov.ru/oos/types/1',
                'no' : 'http://zakupki.gov.ru/oos/export/1'}

  @staticmethod
  def ParseCustomer(customer):
    """Parses customer data from xml subtree"""
    assert len(customer) == 1
    customer = customer[0]
    regNum = customer.xpath('string(oos:regNum)', namespaces=XmlImporter.namespaces)
    fullName = customer.xpath('string(oos:fullName)', namespaces=XmlImporter.namespaces).encode('utf-8')
    inn = customer.xpath('string(oos:inn)', namespaces=XmlImporter.namespaces)
    kpp = customer.xpath('string(oos:kpp)', namespaces=XmlImporter.namespaces)
    tofk = customer.xpath('string(oos:tofk)', namespaces=XmlImporter.namespaces)    
    customer_object = {'regNum':regNum,
                       'fullName':fullName,
                       'inn':inn,
                       'kpp':kpp,
                       'tofk':tofk}
    return customer_object

  @staticmethod
  def ParseSupplier(supplier):
    """Parses supplier data from xml subtree"""
    participantType = supplier.xpath('string(oos:supplier/oos:participantType)', namespaces=XmlImporter.namespaces)
    inn = supplier.xpath('string(oos:supplier/oos:inn)', namespaces=XmlImporter.namespaces)
    kpp = supplier.xpath('string(oos:supplier/oos:kpp)', namespaces=XmlImporter.namespaces)
    organizationForm = supplier.xpath('string(oos:supplier/oos:organizationForm)', namespaces=XmlImporter.namespaces)
    organizationName = supplier.xpath('string(oos:supplier/oos:organizationName)', namespaces=XmlImporter.namespaces).encode('utf-8')
    factualAddress = supplier.xpath('string(oos:supplier/oos:factualAddress)', namespaces=XmlImporter.namespaces).encode('utf-8')
    return {'participantType':participantType,
            'inn':inn,
            'kpp':kpp,
            'organizationForm':organizationForm,
            'organizationName':organizationName,
            'factualAddress':factualAddress}

  def ParseExpense(self, expense):
    date = expense.xpath('string(./oos:protocolDate)', namespaces=XmlImporter.namespaces)
    publishDate = expense.xpath('string(./oos:publishDate)', namespaces=XmlImporter.namespaces)
    publishDate = dateutil.parser.parse(publishDate)
    regNum = expense.xpath('string(./oos:regNum)', namespaces=XmlImporter.namespaces)
    if not date:
      date = expense.xpath('string(./oos:signDate)', namespaces=XmlImporter.namespaces)
    date = date[:-2] + '01'
    price = expense.xpath('number(./oos:price)', namespaces=XmlImporter.namespaces)
    currencyCode = expense.xpath('string(./oos:currency/oos:code)', namespaces=XmlImporter.namespaces)
    if currencyCode != 'RUB':
      print 'Dropping expense not in Rubles, but in %s' % currencyCode
      return []
    customer = XmlImporter.ParseCustomer(expense.xpath('./oos:customer', namespaces=XmlImporter.namespaces))
    self.AddCustomer(customer)
    supplierCount = 0
    for supplierRecord in expense.xpath('./oos:suppliers', namespaces=XmlImporter.namespaces):
      supplier = XmlImporter.ParseSupplier(supplierRecord)
      ++supplierCount
    assert supplierCount < 2 #TODO(vyakunin): can't understand what I do if its false
    self.AddSupplier(supplier)
    products = expense.xpath('./oos:products/oos:product',
                             namespaces=XmlImporter.namespaces)
    
    total = 0.0
    productCount = len(products)
    noSum = False
    results = []
    for product in products:
      okdp = product.xpath('string(./oos:OKDP/oos:code)',
                           namespaces=XmlImporter.namespaces)
      if noSum:
        if okdp != mustOkdp:
          print 'Dropping contract because different OKDP of products without sums %f' % price
          return []
      if (productCount > 1):
        value = product.xpath('number(./oos:sum)',
                              namespaces=XmlImporter.namespaces)
        if math.isnan(value):
          noSum = True
          mustOkdp = okdp
          value = price - total
      else:
        value = price
      total += value
      if value > 0.1 and supplier['inn']:
        results.append({'date':date, 
                        'amount':value,
                        'customer':customer['regNum'],
                        'supplier':supplier['inn'],
                        'region':customer['kpp'][:2],
                        'type':okdp[:2],
                        'regNum':regNum,
                        'publishDate':publishDate})
    
    if abs(total - price) > 1.0:
      print 'Dropping contract with incorrect price: sum for products = %f, while contract price is %f' % (total, price)
      return []
    return results


  def ParseData(self, data):
    """Parses contract.xml in zakupki.gov format

    Args:
      data: File-like object with XML.

    Returns:
      {dict} {spents:[{date, sum, customer, supplier, region, type}],
              customers:[{regNum, fullName, inn, kpp, tofk}],
              suppliers:[{participantType, inn, kpp, organizationForm,
                          organizationName, factualAddress}]}.
    """
    self.suppliers = {}
    self.customers = {}
    spents = []
    tree = etree.parse(data)
    for record in tree.xpath('/no:export/no:contract', namespaces=XmlImporter.namespaces):
      for expense in self.ParseExpense(record):
        spents.append(expense)
    return {'spents': spents,
            'suppliers': self.suppliers,
            'customers': self.customers}

  def AddCustomer(self, customer):
    """Adds customer to dictionary if was absent."""
    if not customer['regNum'] in self.customers:
      self.customers[customer['regNum']] = customer 

  def AddSupplier(self, supplier):
    """Adds supplier to dictionary if was absent."""
    if not supplier['inn'] in self.suppliers: #  TODO(vyakunin): is it correct to use inn as key?
      self.suppliers[supplier['inn']] = supplier

CUSTOMER_MASK_INDEX = 0
SUPPLIER_MASK_INDEX = 1
DATE_MASK_INDEX = 2
REGION_MASK_INDEX =  3
TYPE_MASK_INDEX = 4

def BuildKey(spent, mask):
  key = []
  i = 0
  if mask[i]: # customer
    key.append('0')
  else:
    key.append(spent['customer'])
  i += 1
  if mask[i]: # supplier
    key.append('0')
  else:
    key.append(spent['supplier'])
  i += 1
  if mask[i]: #  date
    key.append('9999-12-31')
  else:
    key.append(spent['date'])
  i += 1
  if mask[i]: #region
    key.append('0')
  else:
    key.append(spent['region'])
  i += 1
  if mask[i]: # type
    key.append('0')
  else:
    key.append(spent['type'])
  return tuple(key)

def BuildMask(mask):
  a = [0, 0, 0, 0, 0]
  aggCount = 0
  for i in range(5):
    a[i] = mask & (1 << i)
    if a[i]:
      aggCount += 1
  return a

def PrintAggregatedForMask(spents, mask, csvWriter):
  aggregatedSpents = {}
  for spent in spents.values():
    key = BuildKey(spent, mask)
    if key in aggregatedSpents:
      aggregatedSpents[key] += spent['amount']
    else:
      aggregatedSpents[key] = spent['amount']
  for key, value in aggregatedSpents.iteritems():
    row = list(key[0:2]) # customer, supplier
    row.append(value) # amount
    row.extend(list(key[2:])) # date, region, type
    csvWriter.writerow(row)

def IsMaskLikeThis(mask, *args):
  """Checks whether the mask aggregates by all fields except *args"""
  not_aggregates = set(args)
  for i, value in enumerate(mask):
    # if value is True we do aggregate
    if (i in not_aggregates) == bool(value):
      return False
  return True

def PrintSpents(spents, filename):
  csvWriter = csv.writer(open(filename, 'wb'), delimiter=',',
                         quotechar='"', quoting=csv.QUOTE_MINIMAL)
  csvWriter.writerow(['customer', 'supplier', 'amount', 'date', 'region', 'type'])
  
  #  TODO(vyakunin): aggregate per date, region, type, customer (9999.12.31)
  for mask in range(1 << 5): #  TODO(vyakunin): palevo
    a = BuildMask(mask)
    # For the time of being we need just several aggregations:
    # * customers
    # * suppliers
    # * spent types
    # * regions
    # * region x date
    # * region x customer
    # * region x supplier
    # * region x type
    if (IsMaskLikeThis(a, CUSTOMER_MASK_INDEX) or
        IsMaskLikeThis(a, SUPPLIER_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX) or
        IsMaskLikeThis(a, TYPE_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX, DATE_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX, CUSTOMER_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX, SUPPLIER_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX, TYPE_MASK_INDEX)):
      PrintAggregatedForMask(spents, a, csvWriter)
  
def PrintCustomers(customers, filename):
  csvWriter = csv.DictWriter(open(filename, 'wb'),
                             ['regNum', 'fullName', 'inn',
                              'kpp', 'tofk'],
                             delimiter=',',
                             quotechar='"',
                             quoting=csv.QUOTE_MINIMAL)
  csvWriter.writerow({'regNum':'reg_num',
                      'fullName':'full_name',
                      'inn':'inn',
                      'kpp':'kpp',
                      'tofk':'tofk'})
  for customer in customers.values():
    csvWriter.writerow(customer)
  
def PrintSuppliers(suppliers, filename):
  csvWriter = csv.DictWriter(open(filename, 'wb'),
                             ['participantType', 'inn',
                              'kpp', 'organizationForm',
                              'organizationName', 'factualAddress'],
                             delimiter=',',
                             quotechar='"',
                             quoting=csv.QUOTE_MINIMAL)
  csvWriter.writerow({'participantType':'participant_type',
                      'inn':'inn',
                      'kpp':'kpp',
                      'organizationForm':'organization_form',
                      'organizationName':'organization_name',
                      'factualAddress':'factual_address'})
  for supplier in suppliers.values():
    if supplier['inn']:
      csvWriter.writerow(supplier)
  
def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], '',
                               ['directory=',
                                'tmpdir=',
                                'outputSpents=',
                                'outputSuppliers=',
                                'outputCustomers='
                                ])
  except getopt.GetoptError, err:
    #print help information and exit:
    print str(err)#  will print something like "option -a not recognized"
    print 'usage: arch -i386 /usr/bin/python data_importer.py --directory="../../Moskovskaja_obl" --tmpdir="../data" --outputSpents="expenses.csv" --outputCustomers="customer.csv" --outputSuppliers="supplier.csv"'
    sys.exit(2)
  for name, value in opts:
    if name == '--directory':
      directory = value
    if name == '--tmpdir':
      tmpdir = value
    elif name == '--outputSpents':
      outputSpents = value 
    elif name == '--outputSuppliers':
      outputSuppliers = value
    elif name == '--outputCustomers':
      outputCustomers = value
  importer = XmlImporter()
  spents = {}
  customers = {}
  suppliers = {}
  for dirname, dirnames, filenames in os.walk(directory):
    for filename in filenames:
      if filename.startswith('contract'):
        filename = os.path.join(dirname, filename)
        assert zipfile.is_zipfile(filename)
        myZip = zipfile.ZipFile(filename, "r")
        for name in myZip.namelist():
          myZip.extract(name, tmpdir)
          inputFile = os.path.join(tmpdir, name)
          print inputFile
          parsed = importer.ParseData(open(inputFile, "r"))
          for spent in parsed['spents']:
            regNum = spent['regNum']
            if (not regNum in spents or 
                (spent['publishDate'] > spents[regNum]['publishDate'])):
              spents[regNum] = spent
             
          for key, value in parsed['customers'].iteritems():
            if not key in customers:
              customers[key] = value
          for key, value in parsed['suppliers'].iteritems():
            if not key in suppliers:
              suppliers[key] = value
          os.remove(inputFile)
            
  PrintSpents(spents, outputSpents)
  PrintCustomers(customers, outputCustomers)
  PrintSuppliers(suppliers, outputSuppliers)

if __name__ == "__main__":
  main()
      
