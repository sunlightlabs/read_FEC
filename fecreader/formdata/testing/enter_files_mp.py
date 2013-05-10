## crap to run this 
import sys, os, time

from django.core.management import setup_environ
sys.path.append('/Users/jfenton/github-whitelabel/read_FEC/fecreader/fecreader/')
sys.path.append('/Users/jfenton/github-whitelabel/read_FEC/fecreader/')

import settings
setup_environ(settings)

###


from multiprocessing import Pool, Process, Queue

from parsing.form_parser import form_parser, ParserMissingError
from parsing.read_FEC_settings import FILECACHE_DIRECTORY
from formdata.utils.filing_processors import process_file



class Worker(Process):
    def __init__(self, queue, id, starttime):
        super(Worker, self).__init__()
        self.queue= queue
        self.id = id
        self.starttime = starttime
        # give each worker it's own fp -- does it need it ? 
        self.fp = form_parser()
        

    def run(self):
        print 'Worker started with id %s' % (self.id)
        # do some initialization here

        for data in iter( self.queue.get, None ):
            # Use data
            print data, self.id
            time.sleep(0.1)
            process_file(data)
            elapsed_time = time.time() - self.starttime
            print "Elapsed time = %s seconds" % (elapsed_time)

            
def get_file_list(filemin=0, list_length=100):
    filecount = 0
    arraylist = []
    for d, _, files in os.walk(FILECACHE_DIRECTORY):
        for a in files:
            filingnum = a.replace(".fec", "")
            if int(filingnum) < filemin:
                continue
            filecount += 1
            if filecount > list_length:
                break
            arraylist.append(filingnum)
    return arraylist
    
                
data_source = get_file_list(767159, 20)
num_threads = 3


print "Timer starting"   
start_time = time.time()

request_queue = Queue()
for i in range(num_threads):
    Worker( request_queue, i , start_time).start()
    
 
for data in data_source:
    request_queue.put( data )
    
    
print "Now shutting down"
# Sentinel objects to allow clean shutdown: 1 per worker.
for i in range(num_threads):
    request_queue.put( None )
    

