#!/usr/bin/python 

import random
import urllib2
import logging
import datetime
import os
import sys
import csv
import re
from collections import OrderedDict

logging.basicConfig(level=logging.INFO)

############################################################# UTILITY for date manipulation

### get beginning year of TWSE
def getFirstYear():
    return 1994

### get the month of date that is beginning of TWSE
def getFirstMonth():
    return 1

### get the day of date that is begninning of TWSE
def getFirstDay():
    return 4

### get month of today
def getThisMonth():
    return datetime.date.today().month

### get year of today
def getThisYear():
    return datetime.date.today().year

### convert TW year unit to AD
def mingo2year(y):
    return 1911+y

### return previous date on calendar
def getPrevDate(d):
    oneday = datetime.timedelta(days=1)
    return d - oneday

### return date obj of yesterday
def getYesterday():
    return getPrevDate(datetime.date.today())


############################################################# UTILITY for file related

### first of all, let's defined some file
### monthly data download from TWSE we call it 'monthly data' 
### we store them in ./data/ with filename <id>_<year>Y_<mm>M.DAT'
###
### after we combine these montly data and we convert it's year to AD year.
### then we store then in ./<id>.db, we call them 'context db', 
### 'cause it would be the only file to store all data.

def genMonthlyDataFilename(stock_id, year, month):
    filename = ('%s_%04dY_%02dM.DAT' % (stock_id, year, month))
    logging.debug('filename: %s' % filename)
    return filename

### we convert downloaded monthly data format yyyy/mm/dd to yyyy-mm-dd
def rawDate2PythonDate(r):
    r = r.strip().split('/')
    r[0] = '%s' % mingo2year(int(r[0]))
    d = '-'.join(r)
    return d




def isEntryExist(ctx, date):
    if date in ctx[1]:
        return True
    else:
        return False

def loadContextDB(stock_id):
    d = dict()
    filename = '%04d.db' % stock_id
    if not os.path.isfile(filename):
        logging.error(' file %s is not valid.' % getDatafileName(stock_id))
        return None
    with open(filename, 'rb') as f:
        csvlines = csv.reader(f, delimiter=',', quotechar='"')
        for row in csvlines:
            d[row[0]] = row[1:]
    f.close()
    logging.info(' context %s was loaded.' % filename)
    return (stock_id, d)

def storeContextDB(d):
    stock_id = d[0]
    data = OrderedDict(sorted(d[1].items(), key=lambda t: t[0]))
    with open('%04d.db' % stock_id, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in data.keys():
            d = data[i]
            d.insert(0, i)
            writer.writerow(d)
    csvfile.close()
    logging.info(' context db %04d.db was saved.' % stock_id)




##############################################################################
############################################################# Major features
##############################################################################

### we download a monthly data file.
def downloadMontlyData(stock_id, y, m):
    if not os.path.isdir('./data'):
        os.mkdir('./data')

    filename = './data/%s' % genMonthlyDataFilename(stock_id, y, m)
    url = 'http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/Report%(yy)d%(mm)02d/%(yy)d%(mm)02d_F3_1_8_%(id)04d.php&type=csv&r=%(rand)s' % {'yy': y, 'mm': m, 'id': stock_id, 'rand':random.randrange(1,1000000)}
    logging.debug('url: %s' % url)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    if len(the_page.split()) >= 3:
        with open(filename, 'w') as f:
            f.write(the_page);
            f.close()
            logging.info(' %s is valid, downloaded and saved.' % filename)
    else:
        logging.error(' no valid data for %s @%04d/%02d' % (stock_id, y, m))

#####################
### TOP_LEVEL API ###
#####################
### we download all monthly data of id from TWSE to ./data/ 
def downloadAllMonthlyData(stock_id):
    if not os.path.isdir('./data'):
        os.mkdir('./data')
    for y in range(getFirstYear(), getThisYear()+1):
        for m in range(1, 13):
            if y == getThisYear() and m > getThisMonth():
                break
            downloadMonthlyData(stock_id, y, m)

#####################
### TOP_LEVEL API ###
#####################
### we combine all monthly data and store into on context db file.
def combineMonthlyData2ContextDB(stock_id):
    datalines = list()
    for y in range(getFirstYear(), getThisYear()+1):
        for m in range(1, 13):
            if y == getThisYear() and m > getThisMonth():
                break
            fn = './data/%s' % genMonthlyDataFilename(stock_id, y, m)
            if os.path.isfile(fn):
                with open(fn, 'r') as f:
                    logging.debug(' loading monthly data file %s' % fn)
                    lines = f.readlines()
                    datalines += lines[2:]
                f.close()
    logging.debug('we got %d lines of data from all monthly data\n' % len(datalines))
    outf = open('%04d.db' % stock_id, 'w')
    for i in datalines:
        i = i.split(',')
        i[0] = rawDate2PythonDate(i[0].strip())  #convert date format.
        outf.write(','.join(i))
    logging.info(' merged as context db file %s' % '%04d.db' % stock_id)

def getBeforeTodayMissing(ctx):
    dd = datetime.date.today()
    if isEntryExist(ctx, dd):
        logging.debug('checking %d data exist...True' % dd)
        return None

    if dd.weekday() >= 5:
        print '%s is weekend, market may be not open today. still download it' % dd

    dates = list()
    delta = datetime.timedelta(days=1)

    while not isEntryExist(ctx, str(dd)):
        dates.append(str(dd))
        dd -= delta
    
    return dates

def updateContextDBFromMonthlyDataFile(ctx, dd):
    ds = dd.split('-')
    (y, m, d) = (int(ds[0]), int(ds[1]), int(ds[2]))
    filename = './data/' + genMonthlyDataFilename(ctx[0], y, m)
    with open(filename, 'rb') as f:
        csvlines = csv.reader(f, delimiter=',', quotechar='"')
        datefmt = re.compile('^[0-9]+\/[0-9]{2}\/[0-9]{2}')
        for row in csvlines:
            if datefmt.match(row[0].strip()):
                if rawDate2PythonDate(row[0]) == dd:
                    logging.info(' found new data @ %s, append to contextDB' % dd)
                    ctx[1][dd] = row[1:]
    f.close()

### To download and fill ContextDB with data up to 'today'
def update2Now(ctx):
    # get year-date to download
    dates = getBeforeTodayMissing(ctx)
    if len(dates) == 0:
        logging.info(' already updated to today.')
        return 1
    download = list()
    for d in dates:
        key = d[0:-3]
        if key not in download:
            logging.info(' need to download this monthly data. @%s' % key)
            download.append(key)
    if len(download) == 0:
        logging.error('internal error')
        return -1
    
    # download/update those montly data file.
    for i in download:
        i = i.split('-')
        downloadMontlyData(ctx[0], int(i[0]), int(i[1]))

    # reading each montly data file and add them into context DB.
    for d in dates:
        updateContextDBFromMonthlyDataFile(ctx, d);
    return 0

context_dbfields_desc = { 'VolumeInUnit':0,  # Trading volume in stock smallest unit
                          'TurnOver$'   :1,  # TurnOver in value $$
                          'Open'        :2,  # openned price
                          'High'        :3,  # highest price
                          'Low'         :4,  # lowest price
                          'Close'       :5,  # closed price
                          'Diff'        :6,  # daily difference in +/-
                          'Transactions':7,  # number of transaction 
                          #-------------- Above are from downloaded data.
                          'Volume'      :8,  # VolumeInUnit/1000 (rounding..)
                          'MA5'         :9,  # Moving average of 5 days
                          'MA10'        :10, #
                          'MA20'        :11, #
                          'MA60'        :12, #
                          'MA120'       :13, #
                          '9K'          :14, #
                          '9D'          :15, #
                      }
rev_context_dbfields_desc = {v: k for k, v in context_dbfields_desc.items()}

def padContextDB(ctx):
    db = ctx[1]
    for k in db.keys():
        n = len(context_dbfields_desc) - len(db[k])
        if n > 0:
            logging.info(' padding context db @ %s %d fields.' % (k, n))
            db[k].extend([None]*n)

def contextIndex2FieldName(i):
    if i in rev_context_dbfields_desc:
        return rev_context_dbfields_desc[i]
    else:
        return None

def contextFieldName2Index(n):
    if n in context_dbfields_desc:
        return context_dbfields_desc[n]
    else:
        return None

    
def contextSetDateValue(ctx, dd, index, value):
    idx = ContextFieldName2Index(index)
    db = ctx[1]
    if dd not in db:
        logging.error(' %s data is missing from context db.' % dd)
    db[dd][idx] = value

def contextGetDateValue(ctx, dd, index):
    idx = contextFieldName2Index(index)
    db = ctx[1]
    if dd not in db:
        logging.error(' @%s data is missing from context db.' % dd)

    return db[dd][idx]

def calculateContextField_Volume(ctx, dd, overwrite):
    index = contextFieldName2Index('Volume');
    db = ctx[1]
    if not overwrite and db[dd][index] != "":
        return
    logging.info(' update volume field in @%s' % dd)

    orig = db[dd][contextFieldName2Index('VolumeInUnit')]
    orig = orig.replace(",", "")
    orig = int(orig)
    value = orig/1000
    if value == 0 and orig != 0:
        value = 1
    else:
        if orig%1000 >= 500:
            value+=1
    db[dd][index] = value

def calculateContextField_MA5(ctx, dd, overwrite):
    index = contextFieldName2Index('MA5');
    db = ctx[1]
    if not overwrite and db[dd][index] != "":
        return
    logging.debug(' update ma5 field in @%s' % dd)

def calculateContextAllFields(ctx):
    db = ctx[1]
    overwrite = False
    for k in db.keys():
        calculateContextField_Volume(ctx, k, overwrite)
        calculateContextField_MA5(ctx, k, overwrite)

#####################
### TOP_LEVEL API ###
#####################
def updateContextDBFileToNow(stock_id):
    ctx = loadContextDB(stock_id)
    if update2Now(ctx) == 0:
        padContextDB(ctx)
        calculateContextAllFields(ctx)
        storeContextDB(ctx)

##### Top level api to download all monthly data of specific id
#downloadAllMonthlyData(int(sys.argv[1]))

##### Top level api to merge monthly data to context db file.
#combineMonthlyData2ContextDB(int(sys.argv[1]))

##### Top level api to update context db file. (Run this daily.)
updateContextDBFileToNow(int(sys.argv[1]))


def test():
    ctx = loadContextDB(2454)
    padContextDB(ctx)
    calculateContextAllFields(ctx)
    storeContextDB(ctx)



#print contextGetDateValue(ctx, str(d), 'High')
#print contextGetDateValue(ctx, str(d), 'Open')
#print contextGetDateValue(ctx, str(d), 'Close')
#print contextGetDateValue(ctx, str(d), 'Low')





#
#def getRawData(stock_id, y, m, d):
#    if not isDatafileValid(stock_id):
#        return 0
#    with open(getDatafileName(stock_id), 'rb') as f:
#        csvlines = csv.reader(f, delimiter=',', quotechar='"')
#        for row in csvlines:
#            if row[0].strip() == '%d/%02d/%02d' % (year2mingo(y), m, d):
#                f.close()
#                return row
#    f.close()

        

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
    print '\t./main.py -n <ID>     to convert to ctx form'

#if len(sys.argv) < 2:
#    usage()
#    exit(0)


# if sys.argv[1] == '-d':
#     downloadAllMonthlyData(int(sys.argv[2]))
# elif sys.argv[1] == '-c':
#     combineMonthlyData2ContextDB(int(sys.argv[2]))
# elif sys.argv[1] == '-n':
#     ctx = loadContextDB(int(sys.argv[2]))
#     dd = datetime.date.today() - datetime.timedelta(days=2)
#     if not isEntryExist(ctx, dd):
#         if dd.weekday() >= 5:
#             print '%s is weekend, market may be not open today.' % dd
#         else:
#             print '%s we need to download latest data' % dd 
#     else:
#         print 'all data is valid'

#     print ctx[0]
#     storeContextDB(ctx)
# else:
#     print '\tPlayground to test new features.'
#     print getYesterday()
#     print getPrevDate(datetime.date(2015,6,1))





