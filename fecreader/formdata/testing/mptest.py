# example adapted from http://stackoverflow.com/a/9039979

# need multiprocessing: 'pip install multiprocessing' 
from multiprocessing import Pool, Process, Queue

class Worker(Process):
    def __init__(self, queue, id):
        super(Worker, self).__init__()
        self.queue= queue
        self.id = id

    def run(self):
        print 'Worker started with id %s' % (self.id)
        # do some initialization here

        for data in iter( self.queue.get, None ):
            # Use data
            print data, self.id
            
the_real_source = range(1,200)

request_queue = Queue()
for i in range(4):
    Worker( request_queue, i ).start()
for data in the_real_source:
    request_queue.put( data )
# Sentinel objects to allow clean shutdown: 1 per worker.
for i in range(4):
    request_queue.put( None )