#!/usr/bin/python

import os
import csv
import re
import datetime
import sys
from collections import OrderedDict

from rutil import ogerutil
from rdate import ogerdate
from rdownload import ogerdownloader

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
    fields = { 'AllVol'      : [0,  None], # Trading volume in stock smallest unit
               'TurnOver'    : [1,  None], # TurnOver in value $$
               'Open'        : [2,  None], # openned price
               'High'        : [3,  None], # highest price
               'Low'         : [4,  None], # lowest price
               'Close'       : [5,  None], # closed price
               'Diff'        : [6,  None], # daily difference in +/-
               'Trans'       : [7,  None], # number of transaction 
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
        self.u  = ogerutil(sid)
        self.d  = ogerdate()
        self.dl = ogerdownloader(sid)
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
            _err('dbfile %s is not valid.' % fn)
            return None
        with open(fn, 'rb') as f:
            csvlines = csv.reader(f, delimiter=',', quotechar='"')
            for row in csvlines:
                self.db[row[0]] = row[1:]
        f.close()
        _info('context %s was loaded.' % fn)
        ###FIXME, we can add pad() here 
        return self.db

    def store(self):
        #data = OrderedDict(sorted(self.db.items(), key=lambda t: t[0]))
        data = self.db
        with open(self.u.dbfile(), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for i in sorted(data.keys()):
                d = data[i]
                d.insert(0, i)
                writer.writerow(d)
        csvfile.close()
        _info('context db %s was saved.' % self.u.dbfile())

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

    ### start from today to check those continus date before that no data
    ### we based on these dates to download and update context db.
    def _getmissingdates(self):
        dd = self.d.today()
        if str(dd) in self.db:
            _info("today's data is updated.")
            return None

        if dd.weekday() >= 5:
            _info('%s is weekend, might no data to update.' % dd)

        dates = list()
        delta = datetime.timedelta(days=1)
        while str(dd) not in self.db:
            dates.append(str(dd))
            dd -= delta
        _debug('those are data missing dates: %s' % str(dates))
        return dates

    def _downloadmissingdata(self):
        dates = self._getmissingdates()
        if dates == None:
            _info('no missing data need to be download')
            return False
        download = list()
        for d in dates:
            key = d[0:-3]
            if key not in download:
                _info('need to download monthly data. @%s' % key)
                download.append(key)
        if len(download) == 0:
            logging.error('internal error')
            return False
        # download/update those montly data file.
        for i in download:
            i = i.split('-')
            self.dl.downloadmonfile(int(i[0]), int(i[1]))
        return dates
        
    def updatemissing(self):
        _info('ID=%04d ready to download and update data up to today.' % self.stock_id)
        dates = self._downloadmissingdata()
        if dates == None:
            _info('no data to be update.')
            return False

        updated = False
        for dd in dates:
            ds = dd.split('-')
            (y, m, d) = (int(ds[0]), int(ds[1]), int(ds[2]))
            fn = self.u.monfile(y,m)
            if not os.path.isfile(fn):
                _warn('file %s not exist. bypass data update.' % fn)
                continue

            with open(fn, 'rb') as f:
                csvlines = csv.reader(f, delimiter=',', quotechar='"')
                datefmt = re.compile('^[0-9]+\/[0-9]{2}\/[0-9]{2}') #yyyy-mm-dd
                for row in csvlines:
                    if datefmt.match(row[0].strip()):
                        if self.d.rawDate2PythonDate(row[0]) == dd:
                            _info('found new data @%s, append to contextDB' % dd)
                            _info('%s' % str(row[1:]))
                            self.db[dd] = row[1:]
                            updated = True
            f.close()
        if updated == False: 
            _info('ID=%04d no data to update.' % self.stock_id)
            return False
        ###FIXME, we should not do calextends() if data update not continusously
        ###FIXME, we need to be able to check the market open dates to do so
        self.pad()
        self.calextends()
        _info('ID=%04d missing data update procedure done.' % self.stock_id)
        self.store()
        return True
        

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


    ### given a date, we return a lists of dates of days
    ###  which market are opened. date included
    def getPrevDates(self, date, days):
        ks = self.db.keys()
        i = ks.index(date)
        if i-days+1 > 0:
            dates = ks[i-days+1:i+1]
        else:
            dates = ks[0:i+1]
        return dates

    def writeoutHtmlHead(self, f):
        out = f.write
        out('<html><head></head></body>\n')
        out('<style>')
        out('td { border: 0px; text-align: right; vertical-align: middle; padding: 15px;')
        out(' font-family:"Open Sans", sans-serif; font-size:16pt; font-weight: bold;}\n')
        out('th { padding: 6px; text-align: right; vertical-align: middle; background-color: #C2C2A3;}\n')
        out('body { font-family: "Open Sans", sans-serif; }\n')
        out('</style>\n')

    def writeoutHtmlTableRow(self, f, ll):
        out = f.write
        out('<tr>\n')
        for i in ll:
            if i == ll[0]:
                out('<td bgcolor="#C2C2A3">%s</td>\n' % i)
            else:
                if '+' in i:
                    out('<td bgcolor="#EBAD99">%s</td>\n' % i)
                elif '-' in i:
                    out('<td bgcolor="#C2FFAD">%s</td>\n' % i)
                else:
                    out('<td>%s</td>\n' % i)
                    
        out('</tr>\n')

    def writeoutHtmlTableRowHeader(self, f, ll):
        out = f.write
        out('<tr>\n')
        for i in ll:
            out('<th>%s</th>\n' % i)
        out('</tr>\n')
        

    ### dump days data into a table.
    def write2html(self, date, days):
        #find dates.
        dates = self.getPrevDates(date, days)
        printed = [5,3,4,2,6,8,15,16]
        f = open("sample.html", "w");
        self.writeoutHtmlHead(f)
        f.write('<font size="32" color="#CC5200"><b>%d</b></font>' % self.stock_id)
        f.write('<table>\n')

        rdates = list()
        for i in dates:
            i = i.split('-')
            i = '%s/%s' % (i[1], i[2])
            rdates.append(i)

        self.writeoutHtmlTableRowHeader(f, [''] + rdates)

        values = list()
        for p in printed:
            del values[:]
            values.append(self.rfields[p])
            for i in dates:
                values.append(self.db[i][p])
            self.writeoutHtmlTableRow(f, values)
        f.write('</table>\n')
        f.write('</body></html>\n')
        f.close();

    def write2htmlx(self, date):
        if date not in self.db:
            _warn('fail to dump. %s not exist' % date)
            return

        f = open(".tmp.html", "w");
        out = f.write

        out('<html><head></head></body>\n')
        out('<style>')
        out('th, td { border: 0px; }\n')
        out('body { font-family: "Open Sans", sans-serif; }')
        out('</style>')

        ks = self.db.keys()
        i = ks.index(date)
        dates = ks[i-2:i+1]
        for dd in reversed(dates):
            out('<br><br><b>%s<b><br>' % str(dd))
            out('<table cellpadding="18">\n')
            t = len(self.rfields)
            div = 10
            b = 0
            e = div
            while b < e:
                out('<tr>\n')
                for i in range(b, e):
                    out('<td bgcolor="#CCCCCC">%s</td>' % self.rfields[i])
                out('</tr>\n')
                out('<tr>\n')
                for i in range(b, e):
                    out('<td bgcolor="#eeeeee">%s</td>' % self.db[dd][i])
                out('</tr>\n')
                b += (div)
                e += (div)
                if e > t:
                    e = t
            out('</table>\n')
        out('</body>\n')
        f.close()

    def dump(self, date, totmpfile=False):
        if date not in self.db:
            _warn('fail to dump. %s not exist' % date)
            return
        if totmpfile:
            f = open(".tmp.dump", "w");
            out = f.write
        else:
            out = sys.stdout.write

        t = len(self.rfields)
        div = 6
        b = 0
        e = div
        sep = ('+' + '-'*17)*div + '+\n'
        sep1 = ('+>>> %s <<' % date) + ('+' + '-'*17)*(div-1) + '+\n'
        while b < e:
            if b == 0:
                out(sep1)
            else:
                out(sep)
            for i in range(b, e):
                out('| %15s ' % self.rfields[i])
            out('|\n')
            for i in range(b, e):
                out('| %15s ' % self.db[date][i])
            out('|\n')
            b += (div)
            e += (div)
            if e > t:
                e = t
        sep = ('+' + '-'*17)*(t%div) + '+\n'
        out(sep)
        if totmpfile:
            f.close()
        
    def dumpdays(self, date, days):
        d = date
        dates = list()
        while True:
            d = str(self.d.getPrevDate(d).date())
            if d  in self.db:
                dates.append(d)
            if len(dates) >= days: break
        for i in reversed(dates):
            self.dump(i)
