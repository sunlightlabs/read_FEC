import csv


from datetime import timedelta,date

#from dateutil.parser import parse as dateparse

from fec_alerts.models import WebK
from summary_data.models import Candidate_Overlay
from parsing.form_parser import form_parser, ParserMissingError


CYCLE = '2014'
this_cycle_start = date(2013,1,1)
one_day = timedelta(days=1)


def write_webk_csv(webk_list, file_name):
    """Given a queryset of webks, write a csv file"""
    outfile = open(file_name, 'w')
    field_list = ['can_id','com_id','com_nam','fil_fre','fec_ele_yea','com_typ','com_des','coverage_from_date','coverage_through_date','tot_dis','tot_loa','tot_rec','cas_on_han_clo_of_per','par_com_con','oth_com_con','tra_fro_oth_aut_com','ind_ite_con','ind_uni_con','can_con','can_loa','oth_loa']
    header = ''
    for i in field_list:
        header = header + i + ", "
    outfile.write(header + "\n")
    csvwriter = csv.DictWriter(outfile, field_list, restval='', extrasaction='ignore')
    # calling values on this--dunno about efficiency. 
    for this_webk in webk_list.values():
        csvwriter.writerow(this_webk)


def summarize_committee_periodic(committee_id, fp=None):

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
    