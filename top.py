#!/usr/bin/python
# coding: utf-8
import rlog
import rutil
import rdate
import sys
import datetime
import time

import os, sys

from rdownload import ogerdownloader
from rcontext import ogercontext
from rdate import ogerdate
from rhtmlwriter import ogerhtmlwriter
from remail import ogeremail
from rtextdump import ogertxtdump
from rutil import ogerutil

import logging
from rlog import ogerlogger
########################################### setup logging primitive
log = ogerlogger('top')
_info  = log.info
_debug = log.debug
_warn  = log.warning
_err   = log.error
_crit  = log.critical

def usage():
    print '\t./stokbot.py update     : update or init db listed in stok.list'
    print ''

def init(stock_id):
    stock_id = int(stock_id)
    d = ogerdownloader(stock_id)
    d.mergemonfile2db()
    d.gendbfile()
    c = ogercontext(stock_id)
    c.load()
    c.pad()
    c.calextends(False)
    c.store()

def update(stock_id):
    stock_id = int(stock_id)
    c = ogercontext(stock_id)
    c.load()
    c.updatemissing()

def resolveDateArg(s):
    if s == 'today':
        d = str(ogerdate().today())
    else:
        d = sys.argv[3]
    return d

def update_all():
    _info('starting daily update procedure..')
    with open('stok.list', 'r') as f:
        ids = f.readlines()
    f.close()
    for i in ids:
        u = ogerutil(i)
            ### TODO, FIXME, this is bad to decide init() by check db file. 
            ### we do immediatedly merge to db when download only one month data....
        if u.isDBFileExist():
            _info('updating #%d' % int(i))
            update(i)
        else:
            _info('initialize #%d' % int(i))
            _info('it may take times to download, please be patient')
            _info('%s' % time.strftime('%c'))
            init(int(i))

def report_all():
    filename = './sample.html'
    w = ogerhtmlwriter()
    w.open(filename)
    w.head()
    with open('stok.list', 'r') as f:
        ids = f.readlines()
    f.close()
    for i in ids:
        c = ogercontext(int(i))
        c.load()
        w.prepare(c)
        w.write(str(ogerdate().today()), 10)
        w.end()
        del c
        _info('data %s have been written into %s' % (i.strip(), filename))
    w.close()
    del w

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        exit(0)

    elif sys.argv[1] == 'update':
        update_all()
    elif sys.argv[1] == 'report':
        report_all()
    elif sys.argv[1] == 'email':
        TO = ['peace.doggie@gmail.com'] #must be a list
        e = ogeremail("", "", "", TO)
        with open('./sample.html', 'rb') as f:
            lines = f.read()
            f.close()
            e.send(lines)

    elif sys.argv[1] == 'dump':
        with open('stok.list', 'r') as f:
            ids = f.readlines()
        f.close()
        for i in ids:
            c = ogercontext(i)
            c.load()
            d = ogertxtdump(c)
            d.dump(resolveDateArg('today'))
            del c
            del d
