## read the zipped file directories to get a maximum and minimum file number for each day. 
# >>> from filerange import filerange
# >>> filerange['20130101']['first']
# '835788'
from datetime import date, timedelta
from urllib2 import Request, urlopen
from os import system, path
import subprocess, time, sys, re


from read_FEC_settings import FEC_FILE_LOCATION, USER_AGENT, ZIP_DIRECTORY, FILECACHE_DIRECTORY, DELAY_TIME



def exec_command(cmd):
    # capture stdout from a unix command
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE  )

    result = ""
    while True:
        #next_line = proc.communicate()[0]
        next_line = proc.stdout.readline()
        if next_line == '' and proc.poll() != None:
            break
        result = result + next_line
        sys.stdout.flush()

    return result
    

start_date =  date(2013,1,1)
end_date = date(2013,6,19)
#end_date = date.today()

one_day = timedelta(days=1)

fileline = re.compile(r'\s+(\d+)\s+(\d\d\d\d-\d\d-\d\d)\s+(\d\d:\d\d)\s+(\d+).fec\n')


this_date = start_date
result_hash = {}
while (this_date < end_date):
    datestring = this_date.strftime("%Y%m%d")
    downloaded_zip_file = ZIP_DIRECTORY + datestring + ".zip"
    cmd = "unzip -l %s" % (downloaded_zip_file)
    print "datestring %s: cmd: %s" % (datestring, cmd)
    this_date += one_day
    if not path.isfile(downloaded_zip_file):
        # a few days are missing--just ignore them
        print "missing dir: %s" % (downloaded_zip_file)
	continue
    result = exec_command(cmd)
    #print result

    
    lines = re.findall(fileline, result)
    numfiles = len(lines)
    if numfiles == 0:
        print "no files found; skipping";

	continue
    firstfile = lines[0][3]
    lastfile = lines[numfiles-1][3]
    
    thisresult = {'first':firstfile, 'last':lastfile, 'length':numfiles}
    print datestring, thisresult
    result_hash[datestring] = thisresult
    
outfile = open("filerange.py", "w")
resultstring = "filerange=" + str(result_hash)
outfile.write(resultstring)
outfile.close()
    
