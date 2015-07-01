#!/usr/bin/python


import logging

class ogerlogger:
    def __init__(self, name, level=logging.INFO):
        self.logger = logging.getLogger(name)
        fmter = logging.Formatter('%(asctime)s %(name)4s [%(levelname)s] %(message)s')
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(fmter)
        self.logger.addHandler(console)
        self.logger.setLevel(level)

    def info(self, args): self.logger.info(args)
    def debug(self, args): self.logger.debug(args)
    def warning(self, args): self.logger.warning(args)
    def error(self, args): self.logger.error(args)
    def critical(self, args): self.logger.critical(args)

    def test(self):
        self.info('test what is this %s %d ' % ('a', 2) )
        self.debug('what')
        self.warning('warnning %s' % 'what the fuck')
 
if __name__ == '__main__':
    olog = ogerlogger('date', logging.DEBUG)
    olog.test()
