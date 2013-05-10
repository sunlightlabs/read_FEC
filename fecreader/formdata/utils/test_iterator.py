# Does psycopg2's cursor suck up all the memory if we feed it tons of data? 
## The answer seems to be -- not if we give the cursor a name. 
## I can't imagine why the cursor having a name determines this behaviour, but... 
# 
# http://initd.org/psycopg/docs/faq.html
# What are the advantages or disadvantages of using named cursors?
#     The only disadvantages is that they use up resources on the server and that there is a little overhead because a at least two queries (one to create the cursor and one to fetch the initial result set) are issued to the backend. The advantage is that data is fetched one chunk at a time: using small fetchmany() values it is possible to use very little memory on the client and to skip or discard parts of the result set.





import psycopg2, time, sys

from cStringIO import StringIO

sys.path.append('/Users/jfenton/github-whitelabel/read_FEC/fecreader/fecreader/')

from local_settings import DATABASES

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

def printout(value):
    if value:
        return str(value)
    return ''

if __name__ == '__main__':
    
    test_output = open('testout.txt', 'w')
    connection = get_connection()
    cursor = connection.cursor("withaname")

#    cmd = "select * from formdata_skeda"
    cmd = "select filing_number, transaction_id, contributor_organization_name, contributor_last_name, contributor_first_name, contributor_city, contributor_state, contributor_zip, contribution_date, contribution_amount, contribution_aggregate, contribution_purpose_code, contribution_purpose_descrip, contributor_employer, contributor_occupation, donor_committee_fec_id, donor_committee_name, donor_candidate_fec_id, donor_candidate_name from formdata_skeda"
    
    t0 = time.time()
    
    cursor.execute(cmd)
    fetchsize = 1000
    ## The cursors an iterator that returns arrays, but we need an iterator that returns strings. 
    
    #for record in cursor:
    while True:
        #print "starting loop"
        temps = StringIO()
        rows = cursor.fetchmany(fetchsize)
        if not rows:
            break
        fr = True
        for row in rows:
            #print row
            temps.write("|".join(printout(i) for i in row) + "\n")
            

        test_output.write(temps.getvalue())
    
    t1 = time.time()
    print "total time = " + str(t1-t0)
        