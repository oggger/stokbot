#!/usr/bin/python 

import os

import logging
from rlog import ogerlogger
########################################### setup logging primitive
log = ogerlogger('util')
_info  = log.info
_debug = log.debug
_warn  = log.warning
_err   = log.error
_crit  = log.critical

class ogerutil:
    def __init__(self, sid): 
        self.stock_id = sid
        
    def stock_id(self, sid): self.stock_id = sid
    def workingdir(self): return "./data/"
    def dbdir(self): return "./db/"

    def monfile(self, year, month):
        filename = (self.workingdir() + '%s_%04dY_%02dM.DAT' % (self.stock_id, year, month))
        _debug('monfile %s' % filename)
        return filename

    def isDBFileExist(self):
        fn = self.dbfile()
        if os.path.exists(fn):
            return True
        else:
            return False

    def dbfile(self):
        filename = self.dbdir() + ('%04d.db' % int(self.stock_id))
        _debug('dbfile %s' % filename)
        return filename
    
    def setupdir(self):
        if not os.path.isdir('./data'):
            _debug('./data was created.')
            os.mkdir('./data')
        if not os.path.isdir('./db'):
            _debug('./db was created.')
            os.mkdir('./db')

if __name__ == '__main__':
    u = ogerutil(2454)
    print u.monfile(2014,5)
    print u.dbfile()
    u.setupdir()
