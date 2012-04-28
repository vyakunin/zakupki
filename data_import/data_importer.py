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
    if date[:4] < '2007':
      print 'Dropping expense older than 2007 year (%s)' % date[:4]
      return []
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

def DumpSpents(writer, spents):
  for spent in spents:
    row = [k.encode('utf-8') for k in [spent['customer'], spent['supplier']]]
    row.append(spent['amount'])
    row.extend([k.encode('utf-8') for k in [spent['date'], spent['region'], spent['type']]])
    row.append(spent['regNum'])
    row.append(spent['publishDate'])
    writer.writerow(row)

def DumpCustomers(writer, customers):
  for customer in customers.values():
    writer.writerow(customer)
  
def DumpSuppliers(writer, suppliers):
  for supplier in suppliers.values():
    if supplier['inn']:
      writer.writerow(supplier)

def DumpData(writers, data):
  DumpSpents(writers['spents'], data['spents'])
  DumpCustomers(writers['customers'], data['customers'])
  DumpSuppliers(writers['suppliers'], data['suppliers'])
  
def InitWriters(outputSpents, outputCustomers, outputSuppliers):
  writers = {}
  spentsWriter = csv.writer(open(outputSpents, 'wb'), delimiter=',',
                         quotechar='"', quoting=csv.QUOTE_MINIMAL)
  spentsWriter.writerow(['customer', 'supplier', 'amount', 'date', 'region', 'type', 'regNum', 'publishDate'])
  writers['spents'] = spentsWriter
  customersWriter = csv.DictWriter(open(outputCustomers, 'wb'),
                                   ['regNum', 'fullName', 'inn',
                                    'kpp', 'tofk'],
                                   delimiter=',',
                                   quotechar='"',
                                   quoting=csv.QUOTE_MINIMAL)
  customersWriter.writerow({'regNum':'reg_num',
                           'fullName':'full_name',
                           'inn':'inn',
                           'kpp':'kpp',
                           'tofk':'tofk'})
  writers['customers'] = customersWriter
  suppliersWriter = csv.DictWriter(open(outputSuppliers, 'wb'),
                                   ['participantType', 'inn',
                                    'kpp', 'organizationForm',
                                    'organizationName', 'factualAddress'],
                                   delimiter=',',
                                   quotechar='"',
                                   quoting=csv.QUOTE_MINIMAL)
  suppliersWriter.writerow({'participantType':'participant_type',
                           'inn':'inn',
                           'kpp':'kpp',
                           'organizationForm':'organization_form',
                           'organizationName':'organization_name',
                           'factualAddress':'factual_address'})
  writers['suppliers'] = suppliersWriter
  return writers

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
    print 'usage: arch -i386 /usr/bin/python data_importer.py --directory="../../Moskovskaja_obl" --tmpdir="../data" --outputSpents="expenses_temp.csv" --outputCustomers="customer.csv" --outputSuppliers="supplier.csv"'
    sys.exit(2)
  for name, value in opts:
    if name == '--directory':
      directory = value
    elif name == '--tmpdir':
      tmpdir = value
    elif name == '--outputSpents':
      outputSpents = value 
    elif name == '--outputSuppliers':
      outputSuppliers = value
    elif name == '--outputCustomers':
      outputCustomers = value
  importer = XmlImporter()
  writers = InitWriters(outputSpents, outputCustomers, outputSuppliers)
  for dirname, dirnames, filenames in os.walk(directory):
    for filename in filenames:
      if filename.startswith('contract'):
        spents = {}
        customers = {}
        suppliers = {}
        filename = os.path.join(dirname, filename)
        assert zipfile.is_zipfile(filename), filename
        myZip = zipfile.ZipFile(filename, "r")
        for name in myZip.namelist():
          myZip.extract(name, tmpdir)
          inputFile = os.path.join(tmpdir, name)
          print inputFile
          parsed = importer.ParseData(open(inputFile, "r"))
          os.remove(inputFile)
          DumpData(writers, parsed)
            
if __name__ == "__main__":
  main()
      
