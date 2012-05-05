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

# Region Data File Name
BASE_FOLDER_REGION = './region_data/'
REGION_NEW = BASE_FOLDER_REGION + 'new_set_output'

# Wild PMs Data File Name
BASE_FOLDER = './data/'
MWD_OUTPUT  = BASE_FOLDER + 'wpm_output'
MWD_UPDATE  = BASE_FOLDER + 'wpm_update'
MWD_RM      = BASE_FOLDER + 'wpm_remove'

# Region
class Region(object):
    def __init__(self):
        self.redis = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)

    # get new regions' set
    def get_new_set(self, p_code_country):
        key = "re:%s" % p_code_country
        if not self.redis.exists(key):
            print('-0- KEY NOT EXISTS')
        new_regions = self.redis.smembers(key)
        print('### OUTPUTING NEW REGIONS...')
        f = open(REGION_NEW , 'a')
        f.write('# TIME - %s\n' % datetime.datetime.now().strftime('%m/%d/%Y - %H:%M'))
        for new_region in new_regions:
            f.write('c:=%s\n' % new_region)
        f.close()


    def add_regions(self):
        if self.redis.hmset("pm:%s" % code, p_pokemon_data):
            print('-1- add region - %s' % code)

    def clean_set(self, p_code_country):
        key = "re:%s" % p_code_country
        if not self.redis.exists(key):
            print('-0- KEY NOT EXISTS')
        if self.redis.delete(key):
            print('-1- Delete for key: %s' % key)



# Wild Pokemon
class WPM(object):
    def __init__(self):
        self.redis = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)

    # do nothing, just output
    def output(self):
        with open(MWD_OUTPUT) as f:
            for KEY in f:
                print('%s | %s' % (str(KEY)[:-1], self.redis.get(str(KEY)[:-1])))

    # update the most widely distributed PMs
    # mwd: Most Widely Distributed
    # <country_code>:mwd
    def update(self):
        with open(MWD_UPDATE) as f:
            for KEY, VALUE in itertools.izip_longest(*[f] * 2):
                self.redis.set(str(KEY)[:-1], str(VALUE)[:-1])
                print('ADD: %s | %s' % (str(KEY)[:-1], self.redis.get(str(KEY)[:-1])))

    # remove
    def remove(self):
        with open(MWD_RM) as f:
            for KEY in f:
                self.redis.delete(str(KEY)[:-1])
                print('RM: %s | %s' % (str(KEY)[:-1], self.redis.get(str(KEY)[:-1])))

# RUN QUEUE
def run_queue():
    # Region
    re = Region()
    re.get_new_set('CN')
    #re.clean_set('CN')
    '''
    # Wild Pokemon
    wpm = WPM()
    wpm.output()
    #wpm.update()
    #wpm.remove()
    '''

if __name__ == '__main__':
    run_queue()
