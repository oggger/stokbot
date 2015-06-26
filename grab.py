#!/usr/bin/python 

import random
import urllib2
import logging

logging.basicConfig(level=logging.INFO)

def writeToFile(filename, msg):
    with open(filename, "w") as f:
        f.write(msg);

########## IT STARTED FROM 1993/1/4
year = 2001
month = 1
stock_id = 2454

def genFilename(stock_id, year, month):
    filename = ('%s_%04dY_%02dM.DAT' % (stock_id, year, month))
    logging.debug('filename: %s' % filename)
    return filename

def genMonthCSVURL(stock_id, year, month):
    url = 'http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/Report%(yy)d%(mm)02d/%(yy)d%(mm)02d_F3_1_8_%(id)04d.php&type=csv&r=%(rand)s' % {'yy': year, 'mm': month, 'id': stock_id, 'rand':random.randrange(1,1000000)}
    logging.debug('url: %s' % url)
    return url

for year in range(1993, 2016):
    for month in range(1, 13):
        filename = genFilename(stock_id, year, month)
        url = genMonthCSVURL(stock_id, year, month)

        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()
        if len(the_page.split()) >= 3:
            writeToFile(filename, the_page);
            logging.info(' %s is valid, downloaded and saved.' % filename)
        else:
            logging.error(' no valid data for %s @%04d/%02d' % (stock_id, year, month))

