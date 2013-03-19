import urllib2
import os
import re

from time import sleep

from read_FEC_settings import FILECACHE_DIRECTORY, USER_AGENT, FEC_DOWNLOAD, DELAY_TIME

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

    # Have we downloaded the file?
    downloaded = False
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
    def __init__(self, filing_number, read_from_cache=True, write_to_cache=False, logger=None):
        self.filing_number = filing_number
        self.headers['filing_number'] = filing_number
        self.read_from_cache = read_from_cache
        self.write_to_cache = write_to_cache
        # This is where we *expect* it--and where it will go if it's not already there
        self.local_file_location = "%s/%s.fec" % (FILECACHE_DIRECTORY, self.filing_number)

    def save_to_cache(self):
        """Save a file to cache."""
        if self.page_read and not os.path.isfile(self.local_file_location):
            local_filing = open(self.local_file_location, "w")
            local_filing.write(self.page_read)
            local_filing.close()

    def _download_with_headers(self):
        """Add a user agent to our download request"""
        url = FEC_DOWNLOAD % (self.filing_number)
        print "url is: %s" % (url)
        headers = {'User-Agent': USER_AGENT}
        req = urllib2.Request(url, None, headers)
        page_read = urllib2.urlopen(req).read()
        sleep(DELAY_TIME)

        self.page_read = page_read
        self.filing_lines = page_read.split("\n")

        # Save it to the file system if it's not there
        if self.write_to_cache:
            self.save_to_cache()

    def _parse_headers(self):
        if self.downloaded:

            header_arr = self.filing_lines[0].split(delimiter)
            summary_line = self.filing_lines[1].split(delimiter)

            # These are always consistent
            self.headers['form'] = clean_entry(summary_line[0])
            self.headers['fec_id'] = clean_entry(summary_line[1])

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
                amendment_match = re.search('^FEC-(\d+)', self.headers['report_id'])
                if amendment_match:
                    original = amendment_match.group(1)
                    #print "Amends filing: %s" % original
                    self.headers['filing_amended'] = original

                else:
                    raise Exception("Can't find original filing in amended report %s" % (self.filing_number))

            else:
                self.is_amendment = False

            self.headers['is_amendment'] = self.is_amendment

        else:
            # We haven't downloaded it. Probably an error(?)
            pass

    def download(self):
        # check if the file is in our cache, if we're reading from cache
        if (self.read_from_cache and os.path.isfile(self.local_file_location)):
            #print "retrieving file %s from cache" % (self.filing_number)
            self.filing_lines = open(self.local_file_location, "r").read().split("\n")
            self.downloaded = True

        else:
            # Don't catch the error if we can't open the filing!
            self._download_with_headers()
            self.downloaded = True

        # Make sense of the headers
        self._parse_headers()

    def get_headers(self):
        """Get a dictionary of file data"""
        return self.headers

    def get_first_row(self):
        return(self.filing_lines[1].split(delimiter))

    def get_raw_first_row(self):
        return(self.filing_lines[1])

    def get_body_rows(self):
        """Get all rows, except the header and the summary"""
        cleaned_array = []
        for i in self.filing_lines[2:]:
            cleaned_array.append(i.split(delimiter))
        return cleaned_array

    def get_rows(self, regex):
        """get all rows that match a regex"""
        results = []
        for i in self.filing_lines:
            if re.match(regex, i):
                results.append(i.split(delimiter))
        return results

    def get_raw_rows(self, regex):
        """Return the rows that match without a delimiter"""
        results = []
        for i in self.filing_lines:
            if re.match(regex, i):
                results.append(i)
        return results

    def get_all_rows(self):
        """get all rows, except the header"""
        results = []
        for i in self.filing_lines[1:]:
            results.append(i.split(delimiter))
        return results

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

# Debugging functions:

    def dump_details(self):
        print "filing_number: %s ; self.headers: %s" % (self.filing_number, self.headers)

    def show_file_contents(self):
        if (self.downloaded):
            print self.filing_lines
        else:
            print "File isn't downloaded!"
