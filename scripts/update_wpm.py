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

BASE_FOLDER = './data/'
MWD         = 'wpm_mwd'

class WPM(object):
    def __init__(self):
        self.redis = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)

    # update the most widely distributed PMs
    # mwd: Most Widely Distributed
    # <country_code>:mwd
    def u_wmd(self):
        with open('%s%s' % (BASE_FOLDER, MWD)) as f:
            for KEY, VALUE in itertools.izip_longest(*[f] * 2):
                self.redis.set(str(KEY)[:-1], str(VALUE)[:-1])
                print('ADD: %s | %s' % (str(KEY)[:-1], self.redis.get(str(KEY)[:-1])))

# RUN QUEUE
def run_queue():
    wpm = WPM()
    wpm.u_wmd() # update Most Widely Distributed

if __name__ == '__main__':
    run_queue()
