import sys

import logging
from rlog import ogerlogger
########################################### setup logging primitive
log = ogerlogger('email')
_info  = log.info
_debug = log.debug
_warn  = log.warning
_err   = log.error
_crit  = log.critical

class ogertxtdump:
    def __init__(self, ctx):
        self.ctx = ctx

    def dump(self, date, totmpfile=False):
        if date not in self.ctx.db:
            _warn('fail to dump. %s not exist' % date)
            return
        if totmpfile:
            f = open(".tmp.dump", "w");
            out = f.write
        else:
            out = sys.stdout.write

        t = len(self.ctx.rfields)
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
                out('| %15s ' % self.ctx.rfields[i])
            out('|\n')
            for i in range(b, e):
                out('| %15s ' % self.ctx.db[date][i])
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
            d = str(self.ctx.d.getPrevDate(d).date())
            if d  in self.ctx.db:
                dates.append(d)
            if len(dates) >= days: break
        for i in reversed(dates):
            self.dump(i)
