# For parts that don't depend on django, we still need a way to get a db connection. 
import psycopg2, sys

sys.path.append('../../')

from fecreader.settings import DATABASES

def get_connection():
    dbname = DATABASES['default']['NAME']
    pw = DATABASES['default']['PASSWORD']
    user = DATABASES['default']['USER']
    host = DATABASES['default']['HOST']
    port = DATABASES['default']['PORT']
    if not host:
        host = 'localhost'
    if not port:
        port = 5432
        
    conn_string = "host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, pw, port)
    conn = psycopg2.connect(conn_string)
    return conn
