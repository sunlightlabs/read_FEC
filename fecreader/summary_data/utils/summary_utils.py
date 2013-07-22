import csv


from datetime import timedelta,date

#from dateutil.parser import parse as dateparse

from fec_alerts.models import WebK
from summary_data.models import Candidate_Overlay, type_hash, committee_designation_hash
from parsing.form_parser import form_parser, ParserMissingError


CYCLE = '2014'
this_cycle_start = date(2013,1,1)
one_day = timedelta(days=1)

filer_type_hash={'Q': 'Quarterly',
          'M': 'Monthly',
          'T': 'Termination report',
          }

def write_webk_csv(webk_list, file_name):
    """Given a queryset of webks, write a csv file"""
    outfile = open(file_name, 'w')
    field_list = ['can_id','com_id','com_nam','fil_fre','fec_ele_yea','com_typ','com_des','coverage_from_date','coverage_through_date','tot_dis','tot_loa','tot_rec','cas_on_han_clo_of_per','par_com_con','oth_com_con','tra_fro_oth_aut_com','ind_ite_con','ind_uni_con','can_con','can_loa','oth_loa']
    human_readable_field_list = ['candidate id (if applicable)','committee id','committee name','filing frequency','Election year (if applicable)','committee type','committee designation','filing start date','filing end date','total disbursements','tot al loans','total receipts','cash on hand close of period','contributions from party committees','contributions from other committees','Transfers received from other affiliated or authorized committees','Individual Itemized Contribution','Individual Unitemized Contribution','Contributions from the candidate (candidate committees only)','Sum of loans from the candidate','Sum of loans from other sources']
    header = ",".join(field_list)
    human_header = ",".join(human_readable_field_list)
    outfile.write(human_header + "\n")
    outfile.write(header + "\n")
    csvwriter = csv.DictWriter(outfile, field_list, restval='', extrasaction='ignore')
    # calling values on this--dunno about efficiency. 
    for this_webk in webk_list.values():
        # use the full text instead of the FEC abbreviations
        
        try:
            this_webk['fil_fre'] = filer_type_hash[this_webk['fil_fre']]
        except KeyError:
            pass        

        try:
            this_webk['com_typ'] = type_hash[this_webk['com_typ']]
        except KeyError:
            pass
        try:
            this_webk['com_des'] = committee_designation_hash[this_webk['com_des']]
        except KeyError:
            pass
        csvwriter.writerow(this_webk)


def summarize_committee_periodic_webk(committee_id, fp=None):

    if not fp:
        fp = form_parser()
    
    relevant_webks = WebK.objects.filter(com_id=committee_id, cycle=CYCLE).order_by('cov_sta_dat')
    if not relevant_webks:
        print "No webks found for id %s" % (committee_id)
    
    # check gaps
    last_end_date = None
    gap_list = []
    for i, wk in enumerate(relevant_webks):
        print i, wk.coverage_from_date, wk.coverage_through_date
        
        if i==0:
            if wk.coverage_from_date - this_cycle_start > one_day:
                print "Missing coverage from start of cycle!!"
                gap_list.append({"gap_start":this_cycle_start, "gap_end":wk.coverage_from_date})
        
        if i>0:
            difference = wk.coverage_from_date - last_end_date
            if difference > one_day:
                print "gap found!"
                gap_list.append({"gap_start":last_end_date, "gap_end":wk.coverage_from_date})
                
        
        
        last_end_date = wk.coverage_through_date
    
    for gap in gap_list:
        print gap
    