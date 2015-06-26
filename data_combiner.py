#!/usr/bin/python 

import datetime
import logging
import os

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

def genFilename(stock_id, year, month):
    filename = ('%s_%04dY_%02dM.DAT' % (stock_id, year, month))
    logging.debug('filename: %s' % filename)
    return filename


stock_id = 2454
outf = open("%s.DAT" % stock_id, "w")
for y in range(getFirstYear(), getThisYear()+1):
    for m in range(1, 13):
        if y == getThisYear() and m > getThisMonth():
            break
        f = "./data/%s" % genFilename(stock_id, y, m)
        if os.path.isfile(f):
            with open(f, "r") as f:
                lines = f.readlines()
            f.close()
            
            for i in lines[2:]:
                outf.write(i)
outf.close()
                
