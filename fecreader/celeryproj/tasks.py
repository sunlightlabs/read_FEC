from __future__ import absolute_import

from celeryproj.celery import celery
from time import sleep
from datetime import datetime
from formdata.utils.filing_body_processor import process_filing_body


@celery.task
def printfile(sleeptime):
    print "Running printfile -- sleeping for %s seconds\n" % (sleeptime)
    sleep(sleeptime)
    # include milliseconds so we know exactly when the task ran
    filename = datetime.now().strftime("%Y_%m_%T_%f").replace(":","_") + ".txt"
    fh = open(filename, 'w')
    fh.write('printfile executed')
    fh.close()



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