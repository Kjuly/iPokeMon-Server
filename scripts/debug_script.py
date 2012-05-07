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

# Region
# re: is for real region DB
# nre: is for new region set that wait to be modified
class Region(object):
    def __init__(self):
        self.redis = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)

    # get new regions' set
    def get_new_set(self, p_code_country):
        key = "nre:%s" % p_code_country
        if not self.redis.exists(key):
            print('-0- KEY NOT EXISTS')
            return
        print('### OUTPUTING NEW REGIONS...')
        # output data to file
        f = open(REGION_NEW , 'a')
        # output time
        f.write('# TIME - %s\n' % datetime.datetime.now().strftime('%m/%d/%Y - %H:%M'))
        # output data
        # format e.g.:
        #   CN=Zhejiang Province=Hangzhou City
        for new_region in self.redis.smembers(key):
            f.write('%s\n' % new_region)
        f.close()
        print('### OUTPUTING NEW REGIONS DONE')

    # add modified(add |code|) regions to DB
    # <re> e.g.:
    #   CN:ZJ:HZ=Zhejiang Province=Hangzhou City
    # re[:8] = CN:ZJ:HZ
    def add_regions(self):
        with open(REGION_NEW) as f:
            print('### SETTING REGION...')
            for re in f:
                re = re[:-1]
                if re[:1] == '#':
                    continue
                self.redis.set('re:%s' % re[:8], re)
                print('-1- SET - re:%s -> %s' % (re[:8], re))
            print('### SETTING REGION DONE')

    # clean new region set
    def clean_set(self, p_code_country):
        key = "nre:%s" % p_code_country
        if not self.redis.exists(key):
            print('-0- KEY NOT EXISTS')
        if self.redis.delete(key):
            print('-1- DELETE - %s' % key)



# RUN QUEUE
def run_queue():
    # Region
    #re = Region()
    #re.get_new_set('CN') # get new region set from DB
    #re.add_regions()     # add modified (|code|) region data to DB, it'll overwrite original key-value pair
    #re.clean_set('CN')   # clean new region set in DB

    # Wild Pokemon
    wpm = WPM()
    #wpm.output()
    wpm.update()
    #wpm.remove()

if __name__ == '__main__':
    run_queue()
