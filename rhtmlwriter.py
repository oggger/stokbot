import sys
from rcontext import ogercontext
import logging
from rlog import ogerlogger
########################################### setup logging primitive
log = ogerlogger('html')
_info  = log.info
_debug = log.debug
_warn  = log.warning
_err   = log.error
_crit  = log.critical

class ogerhtmlwriter:
    def __init__(self):
        self.ctx = None
        self.filename = ""
        self.fd = None

    ### given a date, we return a lists of dates of days
    ###  which market are opened. date included
    def getPrevDates(self, date, days):
        ks = self.ctx.db.keys()
        i = ks.index(date)
        if i-days+1 > 0:
            dates = ks[i-days+1:i+1]
        else:
            dates = ks[0:i+1]
        return dates

    def head(self):
        out = self.fd.write
        out('<html><head></head><body>\n')
        out('<style>')
        out('td { border: 0px; text-align: right; vertical-align: middle; padding: 15px;')
        out(' font-family:"Open Sans", sans-serif; font-size:16pt; font-weight: bold;}\n')
        out('th { padding: 6px; text-align: right; vertical-align: middle; background-color: #C2C2A3;}\n')
        out('body { font-family: "Open Sans", sans-serif; }\n')
        out('</style>\n')

    def tr(self, ll):
        out = self.fd.write
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

    def th(self, ll):
        out = self.fd.write
        out('<tr>\n')
        for i in ll:
            out('<th>%s</th>\n' % i)
        out('</tr>\n')
        

    def open(self, fn):
        self.filename = fn
        self.fd = open(fn, "w");

    def prepare(self, ctx):
        self.ctx = ctx
        self.fd.write('<font size="32" color="#CC5200"><b>%d</b></font>' % self.ctx.stock_id)
        self.fd.write('<table>\n')

    def end(self):
        self.fd.write('</table>\n')

    def close(self):
        self.fd.write('</body></html>\n')
        self.fd.close()

    def write(self, date, days):
        #find dates.
        dates = self.getPrevDates(date, days)
        printed = [5,3,4,2,6,8,15,16]

        rdates = list()
        for i in dates:
            i = i.split('-')
            i = '%s/%s' % (i[1], i[2])
            rdates.append(i)

        self.th([''] + rdates)

        values = list()
        for p in printed:
            del values[:]
            values.append(self.ctx.rfields[p])
            for i in dates:
                values.append(self.ctx.db[i][p])
            self.tr(values)

