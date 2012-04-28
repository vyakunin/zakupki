#!/usr/bin/python2.6
# encoding: utf-8

import csv
import getopt
import sys

CUSTOMER_MASK_INDEX = 0
SUPPLIER_MASK_INDEX = 1
DATE_MASK_INDEX = 2
YEAR_MASK_INDEX = 3
REGION_MASK_INDEX =  4
TYPE_MASK_INDEX = 5

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
    i += 1 # ignore year aggregating if aggregate by date is on
  else:
    i += 1
    if mask[i]: #year
      key.append(spent['date'][:4] + '-12-31')
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
  a = [0, 0, 0, 0, 0, 0]
  for i in range(6):
    a[i] = mask & (1 << i)
  return a

def PrintAggregatedForMask(spents, mask, csvWriter):
  aggregatedSpents = {}
  for spent in spents.values():
    key = BuildKey(spent, mask)
    if key in aggregatedSpents:
      aggregatedSpents[key] += float(spent['amount'])
    else:
      aggregatedSpents[key] = float(spent['amount'])
  for key, value in aggregatedSpents.iteritems():
    row = [k.encode('utf-8') for k in key[0:2]] # customer, supplier
    row.append(value) # amount
    row.extend([k.encode('utf-8') for k in key[2:5]]) # date, region, type
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
  for mask in range(1 << 6): #  TODO(vyakunin): palevo
    a = BuildMask(mask)
    # For the time of being we need just several aggregations:
    # * customers
    # * suppliers
    # * spent types
    # * regions
    # * region x date
    # * region x year TODO(vertix): validate this
    # * region x customer
    # * region x supplier
    # * region x type
    # * customer x type
    # * customer x date
    # * supplier x type
    # * supplier x date
    if (IsMaskLikeThis(a, CUSTOMER_MASK_INDEX) or
        IsMaskLikeThis(a, SUPPLIER_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX) or
        IsMaskLikeThis(a, TYPE_MASK_INDEX) or
        IsMaskLikeThis(a, DATE_MASK_INDEX, YEAR_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX, DATE_MASK_INDEX, YEAR_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX, DATE_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX, CUSTOMER_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX, SUPPLIER_MASK_INDEX) or
        IsMaskLikeThis(a, REGION_MASK_INDEX, TYPE_MASK_INDEX) or
        IsMaskLikeThis(a, CUSTOMER_MASK_INDEX, TYPE_MASK_INDEX) or
        IsMaskLikeThis(a, CUSTOMER_MASK_INDEX, DATE_MASK_INDEX, YEAR_MASK_INDEX) or
        IsMaskLikeThis(a, SUPPLIER_MASK_INDEX, TYPE_MASK_INDEX) or
        IsMaskLikeThis(a, SUPPLIER_MASK_INDEX, DATE_MASK_INDEX, YEAR_MASK_INDEX)):
      PrintAggregatedForMask(spents, a, csvWriter)


def AddSpent(spents, spent):
  regNum = spent['regNum']
  if (not regNum in spents or 
      (spent['publishDate'] > spents[regNum]['publishDate'])):
    spents[regNum] = spent

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], '',
                               ['spentsIn=',
                                'spentsOut=',
                                ])
  except getopt.GetoptError, err:
    #print help information and exit:
    print str(err)#  will print something like "option -a not recognized"
    print '/usr/bin/python aggregator.py --spentsIn="expenses_temp.csv" --spentsOut="expenses.csv"'
    sys.exit(2)
  for name, value in opts:
    if name == '--spentsIn':
      spentsInFile = value
    elif name == '--spentsOut':
      spentsOutFile = value
  inputSpents = csv.DictReader(open(spentsInFile, 'rb'), delimiter=',',
                               quotechar='"')
  spents = {}
  for spent in inputSpents:
    AddSpent(spents, spent)
  PrintSpents(spents, spentsOutFile)
  

if __name__ == "__main__":
  main()
