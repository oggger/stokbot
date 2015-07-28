import datetime
import time
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import logging
from rlog import ogerlogger
########################################### setup logging primitive
log = ogerlogger('email')
_info  = log.info
_debug = log.debug
_warn  = log.warning
_err   = log.error
_crit  = log.critical


class ogeremail:
    def __init__(self, user, pwd, tx, rxlist):
        self.mailsettings = dict()

        key = 'aol'
        (self.username, self.password, self.sendername, self.smtpserver, self.port) = (self.mailsettings[key])
        self.recivers = rxlist
        self.smtpdebug = True

    def send(self, html):
        import smtplib
        TO = self.recivers
        SUBJECT = "Daily StokBot Report %s" % time.strftime('%c')

        msg = MIMEMultipart('alternative')
        #msg = MIMEText(html)
        msg['Subject'] = SUBJECT
        msg['From'] = self.sendername
        msg['To'] = ", ".join(TO)

        part1 = MIMEText("use html-enabled email client.", "plain")
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)

        try:
            _info('setup smtp access @ %s port %d' % (self.smtpserver, self.port))
            server = smtplib.SMTP(self.smtpserver, self.port)
            server.set_debuglevel(self.smtpdebug)
        except:
            _err("something wrong")

        try:
            server.ehlo()
        except:
            _err("ehlo?")

        try:
            server.starttls()
        except:
            _err("ttls?")

        try:
            _info('request to login by %s' % self.username)
            server.login(self.username, self.password)
        except:
            _err("fail to loging?")

        try:
            _info('ready to send mail to %s' % self.recivers)
            server.sendmail(self.sendername, TO, msg.as_string())
        except:
            _err("fail")

        server.quit()
        #server.close()
        _info('successfully sent the mail to %s' % str(TO))
        #except AttributeError as e:
        #    _err(sys.exc_info()[0])
        #    _err(e)
        #    _err('failed to send mail by %s' % self.username)

