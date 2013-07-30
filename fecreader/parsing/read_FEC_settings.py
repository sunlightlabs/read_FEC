CYCLE = '2014'

# where does the FEC keep the daily zip files in bulk ? 
FEC_FILE_LOCATION = "ftp://ftp.fec.gov/FEC/electronic/%s.zip"

# where are the raw .fec files located? 
FEC_DOWNLOAD = "http://query.nictusa.com/dcdev/posted/%s.fec"

FEC_HTML_LOCATION = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/%s/"

# How should our requests be signed? 
USER_AGENT = "FEC READER 0.1; [ YOUR CONTACT INFO HERE ]"

# scraper delay time, in seconds. 
# THIS SHOULD BE AT LEAST 1! THE FEC DOESN'T APPRECIATE FOLKS HITTING THEIR SERVERS TOO HARD, AND WILL BLOCK YOU!
DELAY_TIME=2

LOG_NAME = 'fcc_rss_reader.txt'

try:
    from local_FEC_settings import *
except Exception, e:
    print "Exception in local settings: %s" % (e)
    pass

