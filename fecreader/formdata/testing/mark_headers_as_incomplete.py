# setup
import sys

from django.core.management import setup_environ
sys.path.append('/Users/jfenton/github-whitelabel/read_FEC/fecreader/fecreader/')
sys.path.append('/Users/jfenton/github-whitelabel/read_FEC/fecreader/')

import settings
setup_environ(settings)

## Erase all rows -- run before testing

from django.db import connection, transaction

cursor = connection.cursor()

thiscmd = "update formdata_filing_header set entry_complete = False"
print "\nExecuting command: '%s'" % thiscmd
cursor.execute(thiscmd)
status = cursor.statusmessage
if status:
    print "Result: %s" % status
transaction.commit_unless_managed()


for database_name in ('formdata_skeda', 'formdata_skedb', 'formdata_skede'):
    thiscmd = "delete from %s;" % database_name
    print "\nExecuting command: '%s'" % thiscmd
    cursor.execute(thiscmd)
    status = cursor.statusmessage
    if status:
        print "Result: %s" % status
    transaction.commit_unless_managed()

