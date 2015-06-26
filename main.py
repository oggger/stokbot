#!/usr/bin/python 

import random
import urllib2
import logging
import datetime
import os
import sys
import csv
from collections import OrderedDict

logging.basicConfig(level=logging.INFO)

def getFirstYear():
    return 1994

def getFirstMonth():
    return 1

def getFirstDay():
    return 4

def getThisMonth():
    return datetime.date.today().month

def getThisYear():
    return datetime.date.today().year

def mingo2year(y):
    return 1911+y

def year2mingo(y):
    return y-1911

def genFilename(stock_id, year, month):
    filename = ('%s_%04dY_%02dM.DAT' % (stock_id, year, month))
    logging.debug('filename: %s' % filename)
    return filename

def rawDate2FormalDate(r):
    r = r.split('/')
    r[0] = '%s' % (int(r[0]) + 1911)
    d = '-'.join(r)
    return d
    
def combine_raw_data(stock_id):
    outf = open('%s.DAT' % stock_id, 'w')
    for y in range(getFirstYear(), getThisYear()+1):
        for m in range(1, 13):
            if y == getThisYear() and m > getThisMonth():
                break
            f = './data/%s' % genFilename(stock_id, y, m)
            if os.path.isfile(f):
                with open(f, 'r') as f:
                    lines = f.readlines()
                f.close()
                for i in lines[2:]:
                    outf.write(i)
    outf.close()
                
def writeToFile(filename, msg):
    with open(filename, 'w') as f:
        f.write(msg);
    f.close()

def genMonthCSVURL(stock_id, year, month):
    url = 'http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/Report%(yy)d%(mm)02d/%(yy)d%(mm)02d_F3_1_8_%(id)04d.php&type=csv&r=%(rand)s' % {'yy': year, 'mm': month, 'id': stock_id, 'rand':random.randrange(1,1000000)}
    logging.debug('url: %s' % url)
    return url

def download_raw_data(stock_id):
    for y in range(getFirstYear(), getThisYear()+1):
        for m in range(1, 13):
            if y == getThisYear() and m > getThisMonth():
                break
            filename = './data/%s' % genFilename(stock_id, y, m)
            url = genMonthCSVURL(stock_id, y, m)
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            the_page = response.read()
            if len(the_page.split()) >= 3:
                writeToFile(filename, the_page);
                logging.info(' %s is valid, downloaded and saved.' % filename)
            else:
                logging.error(' no valid data for %s @%04d/%02d' % (stock_id, y, m))

def getDatafileName(stock_id):
    return '%04d.DAT' % stock_id

def isDatafileValid(stock_id):
    if not os.path.isfile(getDatafileName(stock_id)):
        logging.error(' file %s is not valid.' % getDatafileName(stock_id))
        return False
    return True

def getRawData(stock_id, y, m, d):
    if not isDatafileValid(stock_id):
        return 0
    with open(getDatafileName(stock_id), 'rb') as f:
        csvlines = csv.reader(f, delimiter=',', quotechar='"')
        for row in csvlines:
            if row[0].strip() == '%d/%02d/%02d' % (year2mingo(y), m, d):
                f.close()
                return row
    f.close()

def buildContext(stock_id):
    d = dict()
    if not isDatafileValid(stock_id):
        return 0
    with open(getDatafileName(stock_id), 'rb') as f:
        csvlines = csv.reader(f, delimiter=',', quotechar='"')
        for row in csvlines:
            k = row[0].strip()
            d[rawDate2FormalDate(k)] = row[1:]
    f.close()
    return (stock_id, d)

def saveContext2File(d):
    stock_id = d[0]
    data = OrderedDict(sorted(d[1].items(), key=lambda t: t[0]))
    with open('%04d.CSV' % stock_id, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in data.keys():
            d = data[i]
            d.insert(0, i)
            writer.writerow(d)
    csvfile.close()
        

def dumpOneDatum(d):
    print ' +------------------------------+'
    print ' |   Date: %s'       % d[0]
    print ' |   Open: %8s'      % d[3]
    print ' |   High: %8s'      % d[4]
    print ' |    Low: %8s'      % d[5]
    print ' |  Close: %8s (%s)' % (d[6], d[7])
    print ' | Volume: %8s'       % d[8]
    print ' +------------------------------+'

def usage():
    print '\t./main.py -d <ID>     to download all raw'
    print '\t./main.py -c <ID>     to combine raws into one'

if len(sys.argv) < 2:
    usage()
    exit(0)

if sys.argv[1] == '-d':
    download_raw_data(int(sys.argv[2]))
elif sys.argv[1] == '-c':
    combine_raw_data(int(sys.argv[2]))
elif sys.argv[1] == '-t':
    ctx = buildContext(2454)
    print ctx[0]
    saveContext2File(ctx)
    
#    dumpOneDatum(getRawData(2454, 2015, 6, 22))












