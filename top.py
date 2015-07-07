#!/usr/bin/python
# coding: utf-8
import rlog
import rutil
import rdate
import sys
import datetime

import os, sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from rdownload import ogerdownloader
from rcontext import ogercontext
from rdate import ogerdate

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
    print '\t./stokbot.py init   <id>       : download and build <id> db'
    print '\t./stokbot.py update <id>       : update <id> db up to today'
    print '\t./stokbot.py dump <id> <date>  : dump data of <id> at <date>'
    print '\t./stokbot.py dump3 <id> <date> : dump 3days data of <id> at <date>'
    print "\t   <date> can be 'today' or YYYY-MM-DD format"
    print ''

def send_email(sid, html):
            import smtplib
            user = "peacedog911@yahoo.com.tw"
            pwd = ""

            FROM = 'peacedog911@yahoo.com.tw'
            TO = ['peace.doggie@gmail.com', 'smewmew@gmail.com'] #must be a list
            SUBJECT = u"股哥機器人" + (' %04d @ %s' % (sid, str(datetime.date.today())))

            msg = MIMEMultipart('alternative')
            msg['Subject'] = SUBJECT
            msg['From'] = FROM
            msg['To'] = 'MoneyGrabber'

            part1 = MIMEText(html, 'html')
            msg.attach(part1)

            try:
                #server = smtplib.SMTP(SERVER) 
                server = smtplib.SMTP("smtp.mail.yahoo.com", 587) #or port 465 doesn't seem to work!
                server.ehlo()
                server.starttls()
                server.login(user, pwd)
                server.sendmail(FROM, TO, msg.as_string())
                #server.quit()
                server.close()
                print 'successfully sent the mail to %s' % str(TO)
            except AttributeError as e:
                print sys.exc_info()[0]
                print e
                print "failed to send mail"


def resolveDateArg(s):
    if s == 'today':
        d = str(ogerdate().today())
    else:
        d = sys.argv[3]
    return d

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        exit(0)


    
    if sys.argv[1] == 'init':
        sid = int(sys.argv[2])
        d = ogerdownloader(sid)
        d.mergemonfile2db()
        d.gendbfile()
        c = ogercontext(sid)
        c.load()
        c.pad()
        c.calextends(False)
        c.store()
    elif sys.argv[1] == 'update':
        sid = int(sys.argv[2])
        c = ogercontext(sid)
        c.load()
        c.updatemissing()
    elif sys.argv[1] == 'email':
        sid = int(sys.argv[2])
        c = ogercontext(sid)
        c.load()
        d = str(ogerdate().today())
        c.write2html(d,5)
        with open('./sample.html', 'rb') as f:
            lines = f.read()
            f.close()
            send_email(c.stock_id, lines)
    elif sys.argv[1] == 'html':
        sid = int(sys.argv[2])
        c = ogercontext(sid)
        c.load()
        c.write2html(resolveDateArg(sys.argv[3]),5)
    elif sys.argv[1] == 'dump':
        sid = int(sys.argv[2])
        c = ogercontext(sid)
        c.load()
        if sys.argv[3] == 'today':
            d = str(ogerdate().today())
        else:
            d = sys.argv[3]
        c.dump(d)
        c.dump(d, True)
