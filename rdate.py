#!/usr/bin/python

import datetime

class ogerdate:

    def today(self): return datetime.date.today()

    ### get beginning of TWSE
    def getFirstYear(self): return 1994
    def getFirstMonth(self): return 1
    def getFirstDay(self): return 4

    def getThisDay(self): return self.today().day
    def getThisMonth(self): return self.today().month
    def getThisYear(self):  return self.today().year

    ### convert TW year unit to AD
    def mingo2AD(self, y): return 1911+y

    ### return previous date on calendar
    def getPrevDate(self, d):
        oneday = datetime.timedelta(days=1)
        return d - oneday

    ### return date obj of yesterday
    def getYesterday(self): return getPrevDate(self.today())

    ### we convert downloaded data yyyy/mm/dd to yyyy-mm-dd
    def rawDate2PythonDate(self, r):
        if type(r) is not str:
            r = str(r)        
        r = r.strip().split('/')
        if len(r[0]) <= 3:
            r[0] = '%s' % self.mingo2AD(int(r[0]))
        d = '-'.join(r)
        return d

if __name__ == '__main__':
    d = oggerdate()
    print d.rawDate2PythonDate(d.today())
    
