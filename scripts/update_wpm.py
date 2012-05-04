#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import sys, os
from subprocess import Popen, PIPE
import datetime

import redis
from hashlib import md5
import time

import itertools

RADIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB   = 8

# Most Widely Distributed PMs Data File Name
BASE_FOLDER = './data/'
MWD_OUTPUT  = BASE_FOLDER + 'wpm_mwd_output'
MWD_UPDATE  = BASE_FOLDER + 'wpm_mwd_update'
MWD_RM      = BASE_FOLDER + 'wpm_mwd_rm'

# Most Widely Distributed PMs Class
class WPM(object):
    def __init__(self):
        self.redis = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)

    # do nothing, just output
    def output_wmd(self):
        with open(MWD_OUTPUT) as f:
            for KEY in f:
                print('%s | %s' % (str(KEY)[:-1], self.redis.get(str(KEY)[:-1])))

    # update the most widely distributed PMs
    # mwd: Most Widely Distributed
    # <country_code>:mwd
    def update_wmd(self):
        with open(MWD_UPDATE) as f:
            for KEY, VALUE in itertools.izip_longest(*[f] * 2):
                self.redis.set(str(KEY)[:-1], str(VALUE)[:-1])
                print('ADD: %s | %s' % (str(KEY)[:-1], self.redis.get(str(KEY)[:-1])))

    # remove
    def rm_wmd(self):
        with open(MWD_RM) as f:
            for KEY in f:
                self.redis.delete(str(KEY)[:-1])
                print('RM: %s | %s' % (str(KEY)[:-1], self.redis.get(str(KEY)[:-1])))

# RUN QUEUE
def run_queue():
    # Most Widely Distributed
    wpm = WPM()
    wpm.output_wmd()  # output 
    #wpm.update_wmd() # update
    #wpm.rm_wmd()     # remove

if __name__ == '__main__':
    run_queue()
