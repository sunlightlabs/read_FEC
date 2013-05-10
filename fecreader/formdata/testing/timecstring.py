import timeit
from cStringIO import StringIO
import time


t0 = time.time()

a = 'blah'
b = 'craw'

hstore = StringIO()

for i in range(1,1000000):
    hstore.write("\"")
    hstore.write(a)
    hstore.write("\"=>\"")
    hstore.write(b)
    hstore.write("\"")
    
t1 = time.time()

print t1-t0