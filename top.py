#!/usr/bin/python

import rlog
import rutil
import rdate
from rdownload import ogerdownloader
from rcontext import ogercontext

import logging
from rlog import ogerlogger
########################################### setup logging primitive
log = ogerlogger('top')
_info  = log.info
_debug = log.debug
_warn  = log.warning
_err   = log.error
_crit  = log.critical

if __name__ == '__main__':
    ### example to first time download all data.
    #d = ogerdownloader(2454)
    #d.mergemonfile2db()
    #d.gendbfile()

    ### example to calculate extend fields when fresh new dbfile is generated.
    #c = ogercontext(2454)
    #c.load()
    #c.pad()
    #c.calextends(False)
    #c.store()

    d = ogerdownloader(2412)
    d.gendbfile()
    c = ogercontext(2412)
    c.load()
    c.pad()
    c.calextends(False)
    c.store()
