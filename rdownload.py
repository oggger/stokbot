#!/usr/bin/python

import random
import urllib2
import os

from rutil import ogerutil
from rdate import ogerdate

import logging
from rlog import ogerlogger
########################################### setup logging primitive
log = ogerlogger('dl')
_info  = log.info
_debug = log.debug
_warn  = log.warning
_err   = log.error
_crit  = log.critical

class ogerdownloader:
    def __init__(self, sid):
        self.stock_id = sid
        self.u = ogerutil(sid)
        self.d = ogerdate()

    def stock_id(self, sid):
        self.stock_id = sid
        self.u.stock_id(sid)

    ### we download a monthly data file.
    def downloadmonfile(self, y, m):
        self.u.setupdir()
        fn = self.u.monfile(y,m)
        #if os.path.isfile(fn): return #DEBUG, not overwrite
        url = 'http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/Report%(yy)d%(mm)02d/%(yy)d%(mm)02d_F3_1_8_%(id)04d.php&type=csv&r=%(rand)s' % {'yy': y, 'mm': m, 'id': self.stock_id, 'rand':random.randrange(1,1000000)}
        _debug('downloading.. url: %s' %url)
        ###FIXME catch exception and do retry here.
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()
        if len(the_page.split()) >= 3:
            with open(fn, 'w') as f:
                f.write(the_page);
                f.close()
                _info('%s is valid, downloaded and saved.' % fn)
        else:
            _warn('no valid data for %s @%04d/%02d' % (self.stock_id, y, m))

    ### we download all monthly data of id from TWSE to ./data/ 
    def downloadmonfiles(self):
        self.u.setupdir()
        for y in range(self.d.getFirstYear(), self.d.getThisYear()+1):
            for m in range(1, 13):
                if y == self.d.getThisYear() and m > self.d.getThisMonth():
                    break
                self.downloadmonfile(y, m)

    ### we combine all monthly data and store into on context db file.
    def mergemonfile2db(self):
        datalines = list()
        for y in range(self.d.getFirstYear(), self.d.getThisYear()+1):
            for m in range(1, 13):
                if y == self.d.getThisYear() and m > self.d.getThisMonth(): break
                fn = self.u.monfile(y,m)
                if not os.path.isfile(fn): continue
                with open(fn, 'r') as f:
                    _debug('loading monthly data file %s' % fn)
                    lines = f.readlines()
                    datalines += lines[2:] #omit first two line header
                f.close()
        _info('we got %d lines of data from all monthly data' % len(datalines))
        outf = open(self.u.dbfile(), 'w')
        for i in datalines:
            i = i.split(',')
            i[0] = self.d.rawDate2PythonDate(i[0].strip())  #convert date format.
            outf.write(','.join(i))
        _info('merged as context db file %s' % self.u.dbfile())

    def gendbfile(self):
        self.downloadmonfiles()
        self.mergemonfile2db()
