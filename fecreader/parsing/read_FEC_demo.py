from form_parser import form_parser
from filing import filing

# load up a form parser
fp = form_parser()



filingnumbers=(767585, 800502, 808218, 842576, 841933) 

for filingnum in filingnumbers:
    # read from cache if it's available; by default it won't save to cache
    f1 = filing(filingnum, True)
    #f1.download()
    formtype = f1.get_form_type()
    version = f1.version

    print "Got form number %s - type=%s version=%s is_amended: %s" % (f1.filing_number, formtype, version, f1.is_amendment)
    if f1.is_amendment:
        print "Original filing is: %s" % (filing.headers['filing_amended'])
    
    # If it's a F24 save it to cache; this won't overwrite if it's already there
    if formtype=='F24':
        f1.save_to_cache()
    
    if not fp.is_allowed_form(formtype):
        print "skipping form %s - %s isn't parseable" % (f1.filing_number, formtype)
        continue
        
    firstrow = fp.parse_form_line(f1.get_first_row(), version)    
    print "First row is: %s" % (firstrow)
    
    schedule_e_lines = f1.get_rows('SE')
    for e_line in schedule_e_lines:
        firstrow = fp.parse_form_line(e_line, version)        
        print "\nGot sked E line: %s\n" % (firstrow)