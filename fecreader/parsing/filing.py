

import urllib2
import os
import re
from utils import utf8_clean
from time import sleep

from read_FEC_settings import FILECACHE_DIRECTORY

## THIS WON'T WORK ON V 6.0 AND LOWER BECAUSE WE'RE ASSUMING ASCII 28 DELIMITER
# versions used since 1/1/11: 6.4, 7.0, 8.0

# The new FCC files are delimited by ascii 28
delimiter = chr(28)

## adapted from FECH: https://github.com/NYTimes/Fech/blob/master/lib/fech/rendered_maps.rb

## older versions are in here just theoretically
# versions 3-5
old_headers = ['record_type', 'ef_type', 'fec_version', 'soft_name', 'soft_ver', 'name_delim', 'report_id', 'report_number']

# versions 6+
new_headers = ['record_type', 'ef_type', 'fec_version', 'soft_name', 'soft_ver', 'report_id', 'report_number']


# util functions that should go somewhere else
def clean_entry(entry):
    # software called "Trail Blazer" adds quotes, which is shitty
    # See 704636.fec
    return entry.replace('"', "").upper()


class filing(object):


    # FEC-assigned filing number
    filing_number = None
    # What FEC version is it
    version = None

    # Array of filing goes here
    filing_lines = []

    # what's the filing number given in the header?
    is_amendment = None
    # what's the original being amended?
    filing_amended = None
    page_read = None
    headers = {}
    

    # logger's not implemented.
    def __init__(self, filing_number, logger=None):
        self.filing_number = filing_number
        self.headers['filing_number'] = filing_number
        # This is where we *expect* it to be 
        self.local_file_location = "%s/%s.fec" % (FILECACHE_DIRECTORY, self.filing_number)
        
        self.fh = open(self.local_file_location, 'r')
        self.header_row = self.fh.readline().rstrip('\n')
        self.form_row = self.fh.readline().rstrip('\n')
        self.is_error = not self._parse_headers()
        


    def _parse_headers(self):

        header_arr = utf8_clean(self.header_row).split(delimiter)
        summary_line = utf8_clean(self.form_row).split(delimiter)

        # These are always consistent
        try:
            self.headers['form'] = clean_entry(summary_line[0])
            self.headers['fec_id'] = clean_entry(summary_line[1])
            self.headers['report_num'] = None
        except IndexError:
            return False
        
        # amendment number - not sure what version it starts in. 
        if len(summary_line) > 6:
            self.headers['report_num'] = clean_entry(summary_line[6])[:3]

        # Version number is always the third item
        self.version = clean_entry(header_arr[2])
        headers_list = new_headers

        if float(self.version) <= 5:
            headers_list = old_headers

        header_hash = {}
        for i in range(0, len(headers_list)):
            # It's acceptable for header rows to leave off delimiters, so enter missing trailing args as blanks
            this_arg = ""
            try:
                this_arg = clean_entry(header_arr[i])

            except IndexError:
                pass

            self.headers[headers_list[i]] = this_arg

        # figure out if this is an amendment, and if so, what's being amended.
        form_last_char = self.headers['form'][-1].upper()
        if form_last_char == 'A':
            self.is_amendment = True
            #print "Found amendment %s : %s " % (self.filing_number, self.headers['report_id'])
            amendment_match = re.search('^FEC\s*-\s*(\d+)', self.headers['report_id'])
            if amendment_match:
                original = amendment_match.group(1)
                #print "Amends filing: %s" % original
                self.headers['filing_amended'] = original

            else:
                raise Exception("Can't find original filing in amended report %s" % (self.filing_number))

        else:
            self.is_amendment = False

        self.headers['is_amendment'] = self.is_amendment
        return True


    def get_headers(self):
        """Get a dictionary of file data"""
        return self.headers

    def get_error(self):
        """Was there an error?"""
        return self.is_error

    def get_first_row(self):
        return(utf8_clean(self.form_row).split(delimiter))

    def get_raw_first_row(self):
        return(self.form_row)
    
    def get_filer_id(self):
        return self.headers['fec_id']

    def get_body_row(self):
        """get the next body row"""
        next_line = ''
        while True:
            next_line = self.fh.readline()
            
            if next_line:
                if next_line.isspace():
                    continue
                else:
                    return utf8_clean(next_line).split(delimiter)
            else:
                return None

    def get_form_type(self):
        """ Get the base form -- remove the A, N or T (amended, new, termination) designations"""
        try:
            raw_form_type = self.headers['form']
            a = re.search('(.*?)[A|N|T]', raw_form_type)
            if (a):
                return a.group(1)
            else:
                return raw_form_type

        except KeyError:
            return None

    def get_version(self):
        try:
            return self.version
        except KeyError:
            return None

    def dump_details(self):
        print "filing_number: %s ; self.headers: %s" % (self.filing_number, self.headers)



"""


767168 -- 8.2 mb
from filing import filing
a = filing(767168)

"""