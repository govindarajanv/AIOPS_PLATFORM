'''
    ETL.py
    Written By Kyle Chen
    Version 20190325v1
'''

## import buildin pkgs
import sys
import re
import os
import logging
import pandas as pd
from logging.handlers import RotatingFileHandler

## get workpath
workpath = ""
pathlst = re.split(r"\/", sys.path[0])
max_index = len(pathlst) - 1
i = 0

while i < max_index - 1:
    workpath += pathlst[i] + "/"
    i += 1

workpath += pathlst[i]

## append workpath to path
sys.path.append("%s/lib" % (workpath))

## import priviate pkgs
from Config import Config
from Lock import Lock
from GetData import GetData

## ETL Class
class ETL(object):
    ## initial function
    def __init__(self):
        ## set priviate values
        self.config = Config(workpath)
        self.pid = os.getpid()
        self.pname = 'ETL.py'

        ## logger initial
        self.loggerInit()

        ## lock initial
        self.lockObj = Lock(
            self.pname,
            self.pid,
            self.config.LOCK_DIR,
            self.config.LOCK_FILE,
            self.logger)

        ## debug output
        self.logger.debug('ETL Initial Start')
        self.logger.debug('[SYS_CIS][%s]' % (self.config.SYS_CIS))
        self.logger.debug('[MQ_SERVERS][%s]' % (self.config.MQ_SERVERS))
        self.logger.debug('[MQ_QUEUE][%s]' % (self.config.MQ_QUEUE))
        self.logger.debug('[LOCK_DIR][%s]' % (self.config.LOCK_DIR))
        self.logger.debug('[LOCK_FILE][%s]' % (self.config.LOCK_FILE))
        self.logger.debug('[LOG_DIR][%s]' % (self.config.LOG_DIR))
        self.logger.debug('[LOG_FILE][%s]' % (self.config.LOG_FILE))
        self.logger.debug('[LOG_LEVEL][%s]' % (self.config.LOG_LEVEL))
        self.logger.debug('[LOG_MAX_SIZE][%s]' % (self.config.LOG_MAX_SIZE))
        self.logger.debug(
            '[LOG_BACKUP_COUNT][%s]' %
            (self.config.LOG_BACKUP_COUNT))
        self.logger.debug('ETL Initial Done')

    ## initial logger
    def loggerInit(self):
        self.logger = logging.getLogger("ETL")

        try:
            log_level = getattr(logging, self.config.LOG_LEVEL)

        except BaseException:
            log_level = logging.NOTSET

        self.logger.setLevel(log_level)

        fh = RotatingFileHandler(
            self.config.LOG_FILE,
            mode='a',
            maxBytes=self.config.LOG_MAX_SIZE,
            backupCount=self.config.LOG_BACKUP_COUNT)
        fh.setLevel(log_level)

        ch = logging.StreamHandler()
        ch.setLevel(log_level)

        formatter = logging.Formatter(
            '[%(asctime)s][%(name)s][%(levelname)s] %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        return(True)

    ## run asset function
    def run(self):
        self.logger.debug('Getting ETL Data Start')

        ## get data from RabbitMQ
        getDataObj = GetData(self.logger, self.config, self.config.SYS_CIS)
        data = getDataObj.run()

        ## release lock
        self.lockObj.release()

        return(True)

## run it
etlObj = ETL()
etlObj.run()
