#!/usr/bin/python

import rlog
import rutil
import rdate
import sys
import datetime
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

def send_email(sid, msg):
            import smtplib
            gmail_user = "peacedog911@yahoo.com.tw"
            gmail_pwd = "cardigan"
            FROM = 'peacedog911@yahoo.com.tw'
            TO = ['peace.doggie@gmail.com', 'smewmew@gmail.com'] #must be a list
            SUBJECT = "Daily Stokbot repot [%04d] @ %s" % (sid, str(datetime.date.today()))
            TEXT = msg

            # Prepare actual message
            message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
            try:
                #server = smtplib.SMTP(SERVER) 
                server = smtplib.SMTP("smtp.mail.yahoo.com", 587) #or port 465 doesn't seem to work!
                server.ehlo()
                server.starttls()
                server.login(gmail_user, gmail_pwd)
                server.sendmail(FROM, TO, message)
                #server.quit()
                server.close()
                print 'successfully sent the mail'
            except smtplib.SMTPAuthenticationError as e:
                print sys.exc_info()[0]
                print e
                print "failed to send mail"

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
        if sys.argv[3] == 'today':
            d = str(ogerdate().today())
        else:
            d = sys.argv[3]
        c.dump(d, True)
        with open('./.tmp.dump', 'rb') as f:
            lines = f.readlines()
            f.close()
            send_email(c.stock_id, lines)
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
    elif sys.argv[1] == 'dump3':
        sid = int(sys.argv[2])
        c = ogercontext(sid)
        c.load()
        if sys.argv[3] == 'today':
            d = str(ogerdate().today())
        else:
            d = sys.argv[3]
        c.dumpdays(d,3)
    elif sys.argv[1] == 'dump30':
        sid = int(sys.argv[2])
        c = ogercontext(sid)
        c.load()
        if sys.argv[3] == 'today':
            d = str(ogerdate().today())
        else:
            d = sys.argv[3]
        c.dumpdays(d,30)
        
