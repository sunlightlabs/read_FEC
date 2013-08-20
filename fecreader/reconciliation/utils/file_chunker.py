""" Yamlparser can't read big files; so split a file up into single records. Assumes that there's only one top-level identifier, and some other stuff."""

import re

class yamlChunker(object):
    
    # token can be multiple, i.e. 'id|name'
    def __init__(self, file_name, token):
        self.file_name = file_name
        self.fh = open(file_name, 'r')
        # it's a top level identifier, so don't allow leading space
        self.line_regex = re.compile(r'\-\s+' + token + '\s*:\s*\n')
        self.next_line = self.fh.readline()
    
    def next(self):
        
        this_record = self.next_line
        self.next_line = None
        
        while (True):
            thisline = self.fh.readline()
            
            if not thisline:
                # We're at the end of the file
                return this_record
            
            elif re.match(self.line_regex, thisline):
                self.next_line = thisline
                return this_record
                
            else:
                this_record += thisline

