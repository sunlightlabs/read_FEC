"""Load up line parsers for the forms that we care about. By keeping 'em in one central wrapper class we don't have to keep initializing them"""

import re

from line_parser import line_parser

# The new FCC files are delimited by ascii 28
delimiter = chr(28)


class form_parser(object):

    def __init__(self):
        # what forms can we parse?
        self.allowed_forms = {
            'F3': 1,
            'F3X': 1,
            'F3P': 1,
            'F9': 1,
            'F5': 1,
            'F24': 1
        }

        # Init the line parsers for lines we'll need.

        # F3P periodic presidential filing
        f3p = line_parser('F3P')

        # F3X -- periodic pac filing
        f3x = line_parser('F3X')

        # common schedules
        sa = line_parser('SchA')
        sb = line_parser('SchB')
        sc1 = line_parser('SchC1')
        sc2 = line_parser('SchC2')
        sc = line_parser('SchC')
        sd = line_parser('SchD')
        se = line_parser('SchE')
        sf = line_parser('SchF')

        # F24 -- 24 hr ie report
        f24 = line_parser('F24')

        #F9 -- Electioneering communication
        f9 = line_parser('F9')
        f91 = line_parser('F91')
        f92 = line_parser('F92')
        f93 = line_parser('F93')
        f94 = line_parser('F94')

        # IE report by non-committee, roughly
        f5 = line_parser('F5')
        f57 = line_parser('F57')

        # F3 Periodic report for candidate
        f3 = line_parser('F3')
        f3s = line_parser('F3S')

        # Allow text in lines
        text = line_parser('TEXT')

        # match form type to appropriate parsers; must be applied with re.I
        # the leading ^ are redundant if we're using re.match, but...
        self.line_dict = {
            '^SA': sa,
            '^SB': sb,
            '^SC': sc,
            '^SC1': sc1,
            '^SC2': sc2,
            '^SD': sd,
            '^SE': se,
            '^SF': sf,
            '^F3X[A|N|T]': f3x,
            '^F3P[A|N|T]': f3p,
            '^F3S': f3s,
            '^F3[A|N|T]$': f3,
            '^F91': f91,
            '^F92': f92,
            '^F93': f93,
            '^F94': f94,
            '^F9': f9,
            '^F57': f57,
            '^F5': f5,
            '^TEXT': text,
            '^F24': f24
        }

        # we gotta test the regexes in the correct order, and if it's a match pull the line parser from line_dict. Use an array to insure they're tested in the order we want
        # these must be an *EXACT MATCH* to the way they appear in the line_dict above; they are used as the keys.
        self.regex_array = ['^SA', '^SB', '^SC1', '^SC2', '^SC', '^SD', '^SE', '^SF', '^F3X[A|N|T]', '^F3P[A|N|T]', '^F3S', '^F3[A|N|T]$', '^F91', '^F92', '^F93', '^F94', '^F9', '^F57', '^F5', '^TEXT', '^F24']

    # This only checks the top level form name--not the individual lines. This tests the 'base' form as returned by filing.get_form_type() -- i.e. with the trailing A|N|T designator removed.
    def is_allowed_form(self, form_name):
        #print "trying to run %s" % (form_name)
        try:
            self.allowed_forms[form_name]
            return True
        except KeyError:
            #print "Not a parseable form: %s " % (form_name)
            return False

    def parse_form_line(self, line_array, version):

        #print "Trying to parse with v=%s line array=%s " % (version, line_array)
        form_type = line_array[0].replace('"', '').upper()
        #print "parsing form type: %s" % (form_type)
        # Ignore problem lines. Some (most) of these may not be allowed by FEC but have been found in the wild.
        if (form_type == 'H4' or form_type == 'H1' or form_type == 'H2' or form_type =='H3' or form_type == 'H5' or form_type == 'H6' or form_type == 'F3Z'  or form_type == 'F3ZT'  or form_type == 'F3ZA'  or form_type == 'F3ZN' or form_type == 'SL'):
            return None

        for regex in self.regex_array:
            if re.match(regex,form_type, re.I):
                #print "**Got match with regex: %s" % (regex)
                parser = self.line_dict[regex]
                #print "parser = %s" % parser
                parsed_line = parser.parse_line(line_array, version)
                return parsed_line
        
        # Complain if we can't find a parser
        # To do: raise a specific exception so we can catch it elsewhere. 
        raise Exception ("Couldn't find parser for form type %s, v=%s" % (form_type, version))


    def parse_raw_form_line(self, rawline, version):
        line = rawline.split(delimiter)
        return self.parse_form_line(line, version)