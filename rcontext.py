#!/usr/bin/python

import os
import csv
import re
from collections import OrderedDict

from rutil import ogerutil
from rdate import ogerdate

import logging
from rlog import ogerlogger
########################################### setup logging primitive
log = ogerlogger('ctx')
_info  = log.info
_debug = log.debug
_warn  = log.warning
_err   = log.error
_crit  = log.critical


class ogercontext:
    fields = { 'VolumeInUnit': [0,  None], # Trading volume in stock smallest unit
               'TurnOver$'   : [1,  None], # TurnOver in value $$
               'Open'        : [2,  None], # openned price
               'High'        : [3,  None], # highest price
               'Low'         : [4,  None], # lowest price
               'Close'       : [5,  None], # closed price
               'Diff'        : [6,  None], # daily difference in +/-
               'Transactions': [7,  None], # number of transaction 
               #-------------- Above are from downloaded data.
               #-------------- Below are extended fields by ourself
               'Volume'      : [8,  None], # VolumeInUnit/1000 (rounding..)
               'MA5'         : [9,  None], # Moving average of 5 days
               'MA10'        : [10, None], #
               'MA20'        : [11, None], #
               'MA60'        : [12, None], #
               'MA120'       : [13, None], #
               '9RSV'        : [14, None], #
               '9K'          : [15, None], #
               '9D'          : [16, None], #
    }
    rfields = dict()

    def __init__(self, sid):
        self.stock_id = sid
        self.u = ogerutil(sid)
        self.d = ogerdate()
        #build rfields - <n>:'name'
        for i in self.fields:
            self.rfields[self.fields[i][0]] = i

        #we do register all extend fields cal function here...
        self.fields['Volume'][1] = self.calVolume
        self.fields['MA5'][1]    = self.calMA5
        self.fields['MA10'][1]   = self.calMA10
        self.fields['MA20'][1]   = self.calMA20
        self.fields['MA60'][1]   = self.calMA60
        self.fields['MA120'][1]  = self.calMA120
        self.fields['9RSV'][1]   = self.cal9RSV
        self.fields['9K'][1]     = self.cal9K
        self.fields['9D'][1]     = self.cal9D

    def load(self):
        self.db = OrderedDict()
        fn = self.u.dbfile()
        if not os.path.isfile(fn):
            _error('dbfile %s is not valid.' % fn)
            return None
        with open(fn, 'rb') as f:
            csvlines = csv.reader(f, delimiter=',', quotechar='"')
            for row in csvlines:
                self.db[row[0]] = row[1:]
        f.close()
        _info(' context %s was loaded.' % fn)
        ###FIXME, we can add pad() here 
        return self.db

    def store(self):
        #data = OrderedDict(sorted(self.db.items(), key=lambda t: t[0]))
        data = self.db
        with open(self.u.dbfile(), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for i in data.keys():
                d = data[i]
                d.insert(0, i)
                writer.writerow(d)
        csvfile.close()
        _info(' context db %s was saved.' % self.u.dbfile())

    ### because downloaded/updated entries did not include extended fields.
    ### this function will extend db/list to expected fields
    def pad(self):
        n = len(self.fields)
        for k in self.db.keys():
            if n - len(self.db[k]) > 0:
                _info('padding context db @ %s to %d fields.' % (k, n))
                self.db[k].extend([None]*(n - len(self.db[k])))

    ### after padding, we need to update each extend fields value
    def calextends(self, overwrite=False):
        _info('calculate extended fields. %s' % self.stock_id)
        n = len(self.fields)
        for k in self.db.keys():
            for i in range(8, n):
                if overwrite: 
                    self.db[k][i] = self.fields[self.rfields[i]][1](k)
                elif self.db[k][i] == "" or self.db[k][i] == None:
                    self.db[k][i] = self.fields[self.rfields[i]][1](k)

    def stat(self):
        _info('# of days : %d' % len(self.db))

    ###############################################################################
    # do calculation functions below ##############################################
    def calVolume(self, k):
        o = int(self.db[k][0].replace(",",""))
        x = o/1000
        if o%1000 > 500: x += 1
        if x == 0:       x = 1
        return x
    def _calMA(self, k, d):
        #we need to find today and prev 4 close prices.
        ks = self.db.keys()
        i = ks.index(k)
        if i < d: #for those beginning date
            return 0
        s=float(0)
        for i in ks[i-d+1:i+1]:
            s += float(self.db[i][5])
        _debug('cal ma%d @%s %.2f' % (d, k, s/d))
        return round(s/d, 2)
    def calMA5(self, k):  return self._calMA(k,5)
    def calMA10(self,k):  return self._calMA(k,10)
    def calMA20(self,k):  return self._calMA(k,20)
    def calMA60(self,k):  return self._calMA(k,60)
    def calMA120(self,k): return self._calMA(k,120)
    def cal9RSV(self, k):
        ks = self.db.keys()
        i = ks.index(k)
        if i == 0: return 50
        # close - low(9days) / high(9days) - low(9days) * 100
        if i < 9-1: kk = ks[0:i+1]
        else:       kk = ks[i-8:i+1]
        close = float(self.db[k][5])
        low = list()
        high = list()
        for i in kk:
            low.append(float(self.db[i][4]))
            high.append(float(self.db[i][3]))
        hh = max(high)
        ll = min(low)
        rsv = round((close-ll)/(hh-ll)*100,2)
        _debug('cal rsv %.2f' % rsv)
        return rsv
    def cal9K(self,k):
        ks = self.db.keys()
        i = ks.index(k)
        if i == 0: return 50
        rsv = float(self.db[ks[i]][14])
        kk = float(self.db[ks[i-1]][15])
        kkk = (2.0*kk/3.0) + (1.0*rsv/3.0)
        _debug('cal 9k %.2f' % kkk)
        return round(kkk,2)
    def cal9D(self,k):
        ks = self.db.keys()
        i = ks.index(k)
        if i == 0: return 50
        kk = float(self.db[ks[i]][15])
        dd = float(self.db[ks[i-1]][16])
        ddd = (2.0*dd/3.0) + (1.0*kk/3.0)
        _debug('cal 9d %.2f' % ddd)
        return round(ddd,2)
