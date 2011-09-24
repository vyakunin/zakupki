#!/usr/bin/python2.5
# encoding: utf-8
"""
data_importer.py

Copyright (c) Sergey Babenko and Vladimir Yakunin 2011.
All rights reserved.
"""

from lxml import etree
import csv
import getopt
import sys

class XmlImporter(object):
  """Provides iterator over tuples of strings given xml."""

  @staticmethod
  def ParseCustomer(customer, namespaces):
    """Parses customer data from xml subtree"""
    assert len(customer) == 1
    customer = customer[0]
    regNum = customer.xpath('string(oos:regNum)', namespaces=namespaces)
    fullName = customer.xpath('string(oos:fullName)', namespaces=namespaces).encode('utf-8')
    inn = customer.xpath('string(oos:inn)', namespaces=namespaces)
    kpp = customer.xpath('string(oos:kpp)', namespaces=namespaces)
    tofk = customer.xpath('string(oos:tofk)', namespaces=namespaces)    
    return {'regNum':regNum,
            'fullName':fullName,
            'inn':inn,
            'kpp':kpp,
            'tofk':tofk}

  @staticmethod
  def ParseSupplier(supplier, namespaces):
    """Parses supplier data from xml subtree"""
    participantType = supplier.xpath('string(oos:supplier/oos:participantType)', namespaces=namespaces)
    inn = supplier.xpath('string(oos:supplier/oos:inn)', namespaces=namespaces)
    kpp = supplier.xpath('string(oos:supplier/oos:kpp)', namespaces=namespaces)
    organizationForm = supplier.xpath('string(oos:supplier/oos:organizationForm)', namespaces=namespaces)
    organizationName = supplier.xpath('string(oos:supplier/oos:organizationName)', namespaces=namespaces).encode('utf-8')
    factualAddress = supplier.xpath('string(oos:supplier/oos:factualAddress)', namespaces=namespaces).encode('utf-8')
    return {'participantType':participantType,
            'inn':inn,
            'kpp':kpp,
            'organizationForm':organizationForm,
            'organizationName':organizationName,
            'factualAddress':factualAddress}

  def ParseData(self, data):
    """Parses contract.xml in zakupki.gov format

    Args:
      data: File-like object with XML.

    Returns:
      {dict} {spents:[(date, sum, customer, supplier, region)],
              customers:[{regNum, fullName, inn, kpp, tofk}],
              suppliers:[{participantType, inn, kpp, organizationForm,
                          organizationName, factualAddress}]}.
    """
    self.suppliers = {}
    self.customers = {}
    spents = []
    tree = etree.parse(data)

    namespaces = {'oos' : 'http://zakupki.gov.ru/oos/types/1',
                  'no' : 'http://zakupki.gov.ru/oos/export/1'}
    for record in tree.xpath('/no:export/no:contract', namespaces=namespaces):
      date = record.xpath('string(./oos:protocolDate)', namespaces=namespaces)
      if not date:
        date = record.xpath('string(./oos:signDate)', namespaces=namespaces)
      date = date[:-2] + '01'
      amount = record.xpath('number(./oos:price)', namespaces=namespaces)
      currencyCode = record.xpath('string(./oos:currency/oos:code)', namespaces=namespaces)
      assert currencyCode=='RUB'
      customer = XmlImporter.ParseCustomer(record.xpath('./oos:customer', namespaces=namespaces), namespaces)
      self.AddCustomer(customer)
      supplierCount = 0
      for supplierRecord in record.xpath('./oos:suppliers', namespaces=namespaces):
        supplier = XmlImporter.ParseSupplier(supplierRecord, namespaces)
        ++supplierCount
      assert supplierCount < 2 #TODO(vyakunin): can't understand what I do if its false
      self.AddSupplier(supplier)
      spents.append((date, 
                     amount,
                     customer['regNum'],
                     supplier['inn'],
                     customer['inn'][:2]))
    return {'spents': spents,
            'suppliers': self.suppliers.values(),
            'customers': self.customers.values()}

  def AddCustomer(self, customer):
    """Adds customer to dictionary if was absent."""
    if not customer['regNum'] in self.customers:
      self.customers[customer['regNum']] = customer 

  def AddSupplier(self, supplier):
    """Adds supplier to dictionary if was absent."""
    if not supplier['inn'] in self.suppliers: #  TODO(vyakunin): is it correct to use inn as key?
      self.suppliers[supplier['inn']] = supplier

def PrintSpents(spents, filename, aggregate_customer, aggregate_supplier, aggregate_region):
  csvWriter = csv.writer(open(filename, 'wb'), delimiter=',',
                         quotechar='"', quoting=csv.QUOTE_MINIMAL)
  csvWriter.writerow(['customer', 'supplier', 'amount', 'date', 'region'])
  aggregatedSpents = {}
  for spent in spents:
    key = [spent[0]]
    if aggregate_customer: #  TODO(vyakunin): palevo
      key.append('0')
    else:
      key.append(spent[2])
    if aggregate_supplier:
      key.append('0')
    else:
      key.append(spent[3])
    if aggregate_region:
      key.append('0')
    else:
      key.append(spent[4])
    key = tuple(key)
    if key in aggregatedSpents:
      aggregatedSpents[key] += spent[1]
    else:
      aggregatedSpents[key] = spent[1]
  for key, value in aggregatedSpents.iteritems():
    row = list(key[1:3]) # customer, supplier
    row.append(value) # amount
    row.append(key[0]) # date
    row.append(key[3]) # region
    csvWriter.writerow(row)
  
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
  for customer in customers:
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
  for supplier in suppliers:
    csvWriter.writerow(supplier)
  
def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], '',
                               ['input=',
                                'outputSpents=',
                                'outputSuppliers=',
                                'outputCustomers='
                                ])
  except getopt.GetoptError, err:
    #print help information and exit:
    print str(err)#  will print something like "option -a not recognized"
    print 'usage: arch -i386 /usr/bin/python data_importer.py --input="../../contract.xml" --outputSpents="spents.csv" --outputCustomers="customers.csv" --outputSuppliers="suppliers.csv"'
    sys.exit(2)
  for name, value in opts:
    if name == '--input':
      inputFile = value
    elif name == '--outputSpents':
      outputSpents = value 
    elif name == '--outputSuppliers':
      outputSuppliers = value
    elif name == '--outputCustomers':
      outputCustomers = value
  importer = XmlImporter()
  parsed = importer.ParseData(open(inputFile, "r"))
  PrintSpents(parsed['spents'], outputSpents, 
              aggregate_customer=False,
              aggregate_supplier=False,
              aggregate_region=False)
  PrintCustomers(parsed['customers'], outputCustomers)
  PrintSuppliers(parsed['suppliers'], outputSuppliers)

if __name__ == "__main__":
  main()
      
