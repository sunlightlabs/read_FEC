# ASSUMES THAT FILECACHE_DIRECTORY AND ZIP_DIRECTORY EXIST AND ARE WRITEABLE!

BASE_DIR = '.'

# where can we save local files? THIS MUST ALREADY EXIST
FILECACHE_DIRECTORY = BASE_DIR + '/data/fec_filings'

# where can we save raw zip files downloaded from the FEC before unzipping
ZIP_DIRECTORY = BASE_DIR + '/data/zipped_fec_filings'

# where are NYT's csv definitional files? These are generally swiped from here, and fixed up (some of them need tweaking): https://github.com/NYTimes/Fech/tree/master/sources -- or maybe bycoffe's branch: https://github.com/NYTimes/Fech/tree/huffingtonpost/sources
CSV_FILE_DIRECTORY = BASE_DIR + '/sources'



# where does the FEC keep the zip files in bulk ? 
FEC_FILE_LOCATION = "ftp://ftp.fec.gov/FEC/electronic/%s.zip"

# where are the raw .fec files located? 
FEC_DOWNLOAD = "http://query.nictusa.com/dcdev/posted/%s.fec"

# How should our requests be signed? 
#USER_AGENT = "JON'S AMAZING FEC SCRAPER; (555) 555-5555"
USER_AGENT = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"

# scraper delay time, in seconds. 
# THIS SHOULD BE AT LEAST 1! THE FEC DOESN'T APPRECIATE FOLKS HITTING THEIR SERVERS TOO HARD, AND WILL BLOCK YOU!
DELAY_TIME=2


