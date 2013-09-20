from __future__ import absolute_import

from celery import current_task
from time import sleep
from datetime import datetime

from celeryproj.celery import celery

from formdata.utils.filing_body_processor import process_filing_body
from formdata.utils.dump_utils import dump_filing_sked, dump_committee_sked, dump_candidate_sked

import sys
import os
import redis
sys.path.append('../../')


from fecreader.settings import CUSTOM_DOWNLOAD_DIR, CUSTOM_DOWNLOAD_URL

CACHE_TTL = 3600
CACHE_DB = 'files'

r = redis.StrictRedis(host='localhost', port=6379, db=CACHE_DB)

def set_cachekey(key, value):
    r.set(key, value)
    r.expire(key, TTL)

def gzip_file(destination_file):
    gzip_cmd = "gzip -f %s" % (destination_file)
    filename_zipped = destination_file + ".gz"
    proc = os.system(gzip_cmd)
    return filename_zipped

@celery.task
def dump_filing_sked_celery(sked_name, filing_number):
    cache_key = "%s_sked%s" % (filing_number, sked_name)
    result = r.get(cache_key)
    if result:
        print "file cache hit: " + cache_key
        return result
    
    print "file cache miss: " + cache_key
    this_request_id = str(dump_filing_sked_celery.request.id)
    this_request_id = this_request_id.replace("-", "")
    filename = "filing%ssked%s_%s.csv" % (filing_number, sked_name, this_request_id)
    destination_file = CUSTOM_DOWNLOAD_DIR + "/" + filename
    destination_url = CUSTOM_DOWNLOAD_URL + "/" + filename
    dump_filing_sked(sked_name, filing_number, destination_file)
    gzip_file(destination_file)
    destination_url = destination_url + ".gz"
    set_cachekey(cache_key, destination_url)
    return destination_url

@celery.task
def dump_committee_sked_celery(sked_name, committee_number):
    cache_key = "%s_sked%s" % (committee_number, sked_name)
    cached_url = 
    
    this_request_id = dump_committee_sked_celery.request.id
    this_request_id = this_request_id.replace("-", "")
    filename = "%ssked%s_%s.csv" % (committee_number, sked_name, this_request_id)
    destination_file = CUSTOM_DOWNLOAD_DIR + "/" + filename
    destination_url = CUSTOM_DOWNLOAD_URL + "/" + filename
    dump_committee_sked(sked_name, committee_number, destination_file)
    gzip_file(destination_file)
    destination_url = destination_url + ".gz"
    return destination_url


@celery.task
def dump_candidate_sked_celery(sked_name, candidate_id):
    cache_key = "%s_sked%s" % (candidate_id, sked_name)

    this_request_id = dump_candidate_sked_celery.request.id
    this_request_id = this_request_id.replace("-", "")
    filename = "%ssked%s_%s.csv" % (candidate_id, sked_name, this_request_id)
    destination_file = CUSTOM_DOWNLOAD_DIR + "/" + filename
    destination_url = CUSTOM_DOWNLOAD_URL + "/" + filename
    dump_candidate_sked(sked_name, candidate_id, destination_file)
    gzip_file(destination_file)
    destination_url = destination_url + ".gz"
    return destination_url

@celery.task
def process_filing_body_celery(filingnum):
    process_filing_body(filingnum)


@celery.task
def add(x, sked):
    print('Executing task id %r, args: %r kwargs: %r' % (
        add.request.id, add.request.args, add.request.kwargs))
    print('sleeping for 10 seconds')
    sleep(10)
    return x + 1
