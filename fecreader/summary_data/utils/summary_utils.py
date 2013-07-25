import csv


from datetime import timedelta,date


from fec_alerts.models import WebK
from formdata.models import Filing_Header
from summary_data.models import Candidate_Overlay, type_hash, Committee_Time_Summary, committee_designation_hash, Filing_Gap
#from summary_data.models import Committee_Time_Summary


CYCLE = '2014'
this_cycle_start = date(2013,1,1)
one_day = timedelta(days=1)

filer_type_hash={'Q': 'Quarterly',
          'M': 'Monthly',
          'T': 'Termination report',
          }

def set_gap_list(gap_start, gap_end, committee_id):
    # save dictionary of gaps, in chronological order, in an hstore field. 
    filing_gap, created = Filing_Gap.objects.get_or_create(committee_id=committee_id, gap_start=gap_start, gap_end=gap_end)


def write_webk_csv(webk_list, file_name):
    """Given a queryset of webks, write a csv file"""
    outfile = open(file_name, 'w')
    field_list = ['can_id','com_id','com_nam','fil_fre','fec_ele_yea','com_typ','com_des','coverage_from_date','coverage_through_date','tot_dis','tot_loa','deb_owe_by_com','tot_rec','cas_on_han_clo_of_per','par_com_con','oth_com_con','tra_fro_oth_aut_com','ind_ite_con','ind_uni_con','can_con','can_loa','oth_loa']
    human_readable_field_list = ['candidate id (if applicable)','committee id','committee name','filing frequency','Election year (if applicable)','committee type','committee designation','filing start date','filing end date','total disbursements','new loans','outstanding loans','total receipts','cash on hand close of period','contributions from party committees','contributions from other committees','Transfers received from other affiliated or authorized committees','Individual Itemized Contribution','Individual Unitemized Contribution','Contributions from the candidate (candidate committees only)','Sum of loans from the candidate','Sum of loans from other sources']
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



def summarize_committee_periodic_webk(committee_id, force_update=False):
    # Populate the Committee_Time_Summary with webk data. Only do this for the senate. 
    
    relevant_webks = WebK.objects.filter(com_id=committee_id, cov_sta_dat__gte=this_cycle_start).order_by('cov_sta_dat')
    if not relevant_webks:
        print "No webks found for id %s" % (committee_id)
    
    # check gaps
    last_end_date = None
    for i, wk in enumerate(relevant_webks):
        #print i, wk.coverage_from_date, wk.coverage_through_date
        
        if i==0:
            if wk.coverage_from_date:
                if wk.coverage_from_date - this_cycle_start > one_day:
                    set_gap_list(this_cycle_start,wk.coverage_from_date,committee_id)
        
        if i>0:
            difference = wk.coverage_from_date - last_end_date
            if difference > one_day:
                set_gap_list(last_end_date,wk.coverage_from_date,committee_id)
        try:
            this_summary = Committee_Time_Summary.objects.get(com_id=committee_id, coverage_from_date=wk.coverage_from_date, coverage_through_date=wk.coverage_through_date)
            if force_update:
                this_summary.tot_receipts = wk.tot_rec
                this_summary.tot_contrib = wk.tot_con
                this_summary.tot_ite_contrib = wk.ind_ite_con
                this_summary.tot_non_ite_contrib = wk.ind_uni_con
                this_summary.tot_disburse = wk.tot_dis
                this_summary.new_loans = wk.tot_loa
                this_summary.outstanding_loans = wk.deb_owe_by_com
                this_summary.ind_exp_mad = wk.ind_exp_mad
                this_summary.coo_exp_par = wk.coo_exp_par
                this_summary.cash_on_hand_end = wk.cas_on_han_clo_of_per
                this_summary.data_source = 'webk'
                
                this_summary.save()
        
        except Committee_Time_Summary.DoesNotExist:
            Committee_Time_Summary.objects.create(
                com_id=committee_id,
                coverage_from_date=wk.coverage_from_date,
                coverage_through_date=wk.coverage_through_date,
                tot_receipts = wk.tot_rec,
                tot_contrib = wk.tot_con,
                tot_ite_contrib = wk.ind_ite_con,
                tot_non_ite_contrib = wk.ind_uni_con,
                tot_disburse = wk.tot_dis,
                new_loans = wk.tot_loa,
                outstanding_loans = wk.deb_owe_by_com,
                ind_exp_mad = wk.ind_exp_mad,
                coo_exp_par = wk.coo_exp_par,
                cash_on_hand_end = wk.cas_on_han_clo_of_per,
                data_source = 'webk'
            )
        
        
        last_end_date = wk.coverage_through_date




# from summary_data.utils.summary_utils import summarize_committee_periodic_webk
# summarize_committee_periodic_webk('C00003251')




# routines to standardize the variables present in different filings. Sigh. 
def map_f3x_to_cts(f3p_dict):
    cts_dict = {
        'tot_receipts':f3p_dict.get('col_a_total_receipts'),
        'tot_ite_contrib':f3p_dict.get('col_a_individuals_itemized'), #*
        'tot_non_ite_contrib':f3p_dict.get('col_a_individuals_unitemized'), #*
        'tot_disburse':f3p_dict.get('col_a_total_disbursements'),
        'ind_exp_mad':f3p_dict.get('col_a_independent_expenditures'), #
        'coo_exp_par':f3p_dict.get('col_a_coordinated_expenditures_by_party_committees'), # na for form 3
        'new_loans':f3p_dict.get('col_a_total_loans'),
        'outstanding_loans':f3p_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        'cash_on_hand_end':f3p_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict

def map_f3_to_cts(f3p_dict):
    cts_dict = {
        'tot_receipts':f3p_dict.get('col_a_total_receipts'),
        'tot_ite_contrib':f3p_dict.get('col_a_individual_contributions_itemized'),
        'tot_non_ite_contrib':f3p_dict.get('col_a_individual_contributions_unitemized'),
        'tot_disburse':f3p_dict.get('col_a_total_disbursements'),
        'ind_exp_mad':0, # na for form 3
        'coo_exp_par':0, # na for form 3
        'new_loans':f3p_dict.get('col_a_total_loans'),
        'outstanding_loans':f3p_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        'cash_on_hand_end':f3p_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict

def map_f3p_to_cts(f3p_dict):
    cts_dict = {
        'tot_receipts':f3p_dict.get('col_a_total_receipts'),
        'tot_ite_contrib':f3p_dict.get('col_a_individuals_itemized'), #*
        'tot_non_ite_contrib':f3p_dict.get('col_a_individuals_unitemized'), #*
        'tot_disburse':f3p_dict.get('col_a_total_disbursements'),
        'ind_exp_mad':0, # na for form 3
        'coo_exp_par':0, # na for form 3
        'new_loans':f3p_dict.get('col_a_total_loans'),
        'outstanding_loans':f3p_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        'cash_on_hand_end':f3p_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict

def string_to_float(the_string):
    # Return zero if it's a blank space
    s = the_string.rstrip()
    if s:
        return float(s)
    else:
        return 0
        
def summarize_committee_periodic_electronic(committee_id, force_update=False):
    relevant_filings = Filing_Header.objects.filter(raw_filer_id=committee_id, is_superceded=False, coverage_from_date__gte=date(2013,1,1), form__in=['F3P', 'F3', 'F3X']).order_by('coverage_from_date')
    #print "processing %s" % committee_id
    if not relevant_filings:
        #print "No filings found for %s" % (committee_id)
        return None
    
    # check gaps
    last_end_date = None
    for i, this_filing in enumerate(relevant_filings):
        #print i, this_filing.coverage_from_date, this_filing.coverage_through_date
        if i==0:
            if this_filing.coverage_from_date - this_cycle_start > one_day:
                #print "Missing coverage from start of cycle!!"
                set_gap_list(this_cycle_start,this_filing.coverage_from_date, committee_id)
                
        
        if i>0:
            difference = this_filing.coverage_from_date - last_end_date
            if difference > one_day:
                #print "gap found!"
                set_gap_list(last_end_date,this_filing.coverage_from_date, committee_id)

        #print "Got filing %s - %s" % (this_filing.coverage_from_date, this_filing.coverage_through_date)
        
        last_end_date = this_filing.coverage_through_date
        form = this_filing.form
        header_data = this_filing.header_data
        cts_dict = {}
        if form == 'F3':
            cts_dict = map_f3_to_cts(header_data)
        elif form == 'F3P':
            cts_dict = map_f3p_to_cts(header_data)
        elif form == 'F3X':
            cts_dict = map_f3x_to_cts(header_data)
        
        
        tot_contribs = string_to_float(cts_dict['tot_ite_contrib']) + string_to_float(cts_dict['tot_non_ite_contrib'])

        cts_dict['filing_number'] = this_filing.filing_number
        cts_dict['coverage_through_date'] = this_filing.coverage_through_date
        cts_dict['coverage_from_date'] = this_filing.coverage_from_date
        cts_dict['data_source'] = 'electronic'
        cts_dict['com_id'] = committee_id
        cts_dict['tot_contrib'] = tot_contribs 
        
        for i in cts_dict:
            if cts_dict[i] == '':
                cts_dict[i] = None
            
        
        try:
            this_summary = Committee_Time_Summary.objects.get(com_id=committee_id, coverage_from_date=this_filing.coverage_from_date, coverage_through_date=this_filing.coverage_through_date)
            if force_update:

                this_summary.filing_number = this_filing.filing_number
                this_summary.tot_receipts = cts_dict.get('tot_receipts')
                this_summary.tot_ite_contrib = cts_dict.get('tot_ite_contrib')
                this_summary.tot_non_ite_contrib = cts_dict.get('tot_non_ite_contrib')
                this_summary.tot_contrib = cts_dict.get('tot_contrib')
                this_summary.tot_disburse = cts_dict.get('tot_disburse')
                this_summary.new_loans = cts_dict.get('new_loans')
                this_summary.outstanding_loans = cts_dict.get('outstanding_loans')
                this_summary.ind_exp_mad = cts_dict.get('ind_exp_mad')
                this_summary.coo_exp_par = cts_dict.get('coo_exp_par')
                this_summary.cash_on_hand_end = cts_dict.get('cash_on_hand_end')
                this_summary.data_source = cts_dict.get('data_source')
                this_summary.save()
                
        except Committee_Time_Summary.DoesNotExist:
            cts = Committee_Time_Summary(**cts_dict)
            cts.save()




# from summary_data.utils.summary_utils import summarize_committee_periodic_electronic
# summarize_committee_periodic_electronic('C00003251')


