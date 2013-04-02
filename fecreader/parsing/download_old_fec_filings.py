""" Util to download the zipped, raw fec files from the FEC ftp site and unzip them directly to the filecache directory. If we do this ahead of time, we don't need to hit their site tons of times to backfill / analyze older data. Assumes we can use unzip at the cmd prompt... """

from datetime import date, timedelta
from urllib2 import Request, urlopen
from os import system
from time import sleep

from read_FEC_settings import FEC_FILE_LOCATION, USER_AGENT, ZIP_DIRECTORY, FILECACHE_DIRECTORY, DELAY_TIME

# Note that 2011/12/04, 2012/07/01, 2012/12/15, 2012/12/25 do not exist; presumably no filings were received on these days.

# todo: take these as cmd line args--but do I really wanna deal with parsing 'em? 
start_date = date(2012,12,26)
end_date = date(2012,12,31)

one_day = timedelta(days=1)


def download_with_headers(url):
    """ Sign our requests with a user agent set in the settings file"""
    headers = { 'User-Agent' : USER_AGENT }    
    req = Request(url, None, headers)
    return urlopen(req).read()

this_date = start_date
while (this_date < end_date):
    datestring = this_date.strftime("%Y%m%d")
    file_to_download = FEC_FILE_LOCATION % datestring
    print "Downloading: %s" % (file_to_download)
    this_date += one_day
    downloaded_zip_file = ZIP_DIRECTORY + "/" + datestring + ".zip"
    dfile = open(downloaded_zip_file, "w")
    dfile.write(download_with_headers(file_to_download))
    dfile.close()
    
    # Now unzip 'em 
    cmd = "unzip -o %s -d %s" % (downloaded_zip_file, FILECACHE_DIRECTORY)
    print "Now unzipping with %s" % (cmd)
    system(cmd)
    
    # Pause 
    print "Now sleeping for a %s second(s)" % (DELAY_TIME)
    sleep(DELAY_TIME)
