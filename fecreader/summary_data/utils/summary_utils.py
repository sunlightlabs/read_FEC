import csv


from datetime import timedelta,date
from django.db.models import Sum


from fec_alerts.models import WebK
from ftpdata.models import Committee
from fec_alerts.models import new_filing
from summary_data.models import Candidate_Overlay, Committee_Overlay, type_hash, Committee_Time_Summary, committee_designation_hash, Filing_Gap


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


def write_new_committee(new_committee_queryset, file_name):
    outfile = open(file_name, 'w')
    field_list = ['fec_id', 'ctype', 'name', 'date_filed']
    header = ",".join(field_list)
    outfile.write(header + "\n")
    csvwriter = csv.DictWriter(outfile, field_list, restval='', extrasaction='ignore')
    for new_committee in new_committee_queryset.values():
        try:
            new_committee['ctype'] = type_hash[new_committee['ctype']]
        except KeyError:
            pass
        csvwriter.writerow(new_committee)
        
    
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


def write_all_candidates(file_name):
    outfile = open(file_name, 'w')
    field_list = ['is_incumbent','cycle','not_seeking_reelection','other_office_sought','other_fec_id','name','pty','party','fec_id','pcc','election_year','state','office','office_district','term_class','total_receipts','total_contributions','total_disbursements','outstanding_loans','cash_on_hand','cash_on_hand_date','total_expenditures','expenditures_supporting','expenditures_opposing']
    human_readable_field_list = ['is_incumbent', 'cycle ', 'not_seeking_reelection', 'other_office_sought ', 'other_fec_id ', 'name', 'pty ', 'party ', 'fec_id ', 'pcc ', 'election_year', 'state', 'office', 'office_district', 'term_class', 'total_receipts', 'total_contributions', 'total_disbursements', 'outstanding_loans', 'cash_on_hand', 'cash_on_hand_date', 'total_independent_expenditures', 'independent_expenditures_supporting', 'independent_expenditures_opposing']
    header = ",".join(field_list)
    human_header = ",".join(human_readable_field_list)
    outfile.write(human_header + "\n")
    #outfile.write(header + "\n")
    csvwriter = csv.DictWriter(outfile, field_list, restval='', extrasaction='ignore')
    # calling values on this--dunno about efficiency. 
    candidates = Candidate_Overlay.objects.all()
    for candidate in candidates.values():
        
        csvwriter.writerow(candidate)


def write_all_webks(file_name):
    webks = WebK.objects.filter(cycle='2014')
    write_webk_csv(webks, file_name)


def summarize_committee_periodic_webk(committee_id, force_update=False):
    # Populate the Committee_Time_Summary with webk data. Only do this for the senate. 
    
    relevant_webks = WebK.objects.filter(com_id=committee_id, cov_sta_dat__gte=this_cycle_start).order_by('cov_sta_dat')
    if not relevant_webks:
        print "No webks found for id %s" % (committee_id)
    
    # check gaps
    last_end_date = None
    for i, wk in enumerate(relevant_webks):
        #print i, wk.coverage_from_date, wk.coverage_through_date
        
        
        
        """
        if i==0:
            if wk.coverage_from_date:
                if wk.coverage_from_date - this_cycle_start > one_day:
                    set_gap_list(this_cycle_start,wk.coverage_from_date,committee_id)
        
        if i>0:
            difference = wk.coverage_from_date - last_end_date
            if difference > one_day:
                set_gap_list(last_end_date,wk.coverage_from_date,committee_id)
                
        """
        
        try:
            this_summary = Committee_Time_Summary.objects.get(com_id=committee_id, coverage_from_date=wk.coverage_from_date, coverage_through_date=wk.coverage_through_date)
            if force_update:
                this_summary.tot_receipts = wk.tot_rec
                this_summary.com_name = wk.com_nam
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
            print "Creating webk for %s: %s - %s" % (wk.com_nam, wk.coverage_from_date, wk.coverage_through_date)
            Committee_Time_Summary.objects.create(
                com_id=committee_id,
                coverage_from_date=wk.coverage_from_date,
                coverage_through_date=wk.coverage_through_date,
                tot_receipts = wk.tot_rec,
                com_name = wk.com_nam, 
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
def map_f3x_to_cts(this_dict):
    cts_dict = {
        'tot_receipts':this_dict.get('col_a_total_receipts'),
        'tot_ite_contrib':this_dict.get('col_a_individuals_itemized'), #*
        'tot_non_ite_contrib':this_dict.get('col_a_individuals_unitemized'), #*
        'tot_disburse':this_dict.get('col_a_total_disbursements'),
        'ind_exp_mad':this_dict.get('col_a_independent_expenditures'), #
        'coo_exp_par':this_dict.get('col_a_coordinated_expenditures_by_party_committees'), # na for form 3
        'new_loans':this_dict.get('col_a_total_loans'),
        'outstanding_loans':this_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        'cash_on_hand_end':this_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict

def map_f5_to_cts(this_dict):
    cts_dict = {
        'tot_receipts':this_dict.get('total_contribution'),
        # 'tot_ite_contrib': F5 doesn't have this line
        #'tot_non_ite_contrib':this_dict.get('col_a_individuals_unitemized'), #*
        'tot_disburse':this_dict.get('total_independent_expenditure'),
        'ind_exp_mad':this_dict.get('total_independent_expenditure'), #
        'coo_exp_par':0, # na for form 3
        #'new_loans':this_dict.get('col_a_total_loans'),
        #'outstanding_loans':this_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        #'cash_on_hand_end':this_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict


def map_f3_to_cts(this_dict):
    cts_dict = {
        'tot_receipts':this_dict.get('col_a_total_receipts'),
        'tot_ite_contrib':this_dict.get('col_a_individual_contributions_itemized'),
        'tot_non_ite_contrib':this_dict.get('col_a_individual_contributions_unitemized'),
        'tot_disburse':this_dict.get('col_a_total_disbursements'),
        'ind_exp_mad':0, # na for form 3
        'coo_exp_par':0, # na for form 3
        'new_loans':this_dict.get('col_a_total_loans'),
        'outstanding_loans':this_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        'cash_on_hand_end':this_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict

def map_f3p_to_cts(this_dict):
    cts_dict = {
        'tot_receipts':this_dict.get('col_a_total_receipts'),
        'tot_ite_contrib':this_dict.get('col_a_individuals_itemized'), #*
        'tot_non_ite_contrib':this_dict.get('col_a_individuals_unitemized'), #*
        'tot_disburse':this_dict.get('col_a_total_disbursements'),
        'ind_exp_mad':0, # na for form 3
        'coo_exp_par':0, # na for form 3
        'new_loans':this_dict.get('col_a_total_loans'),
        'outstanding_loans':this_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        'cash_on_hand_end':this_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict

def string_to_float(the_string):
    # Return zero if it's a blank space
    if not the_string:
        return 0
    s = the_string.rstrip()
    if s:
        return float(s)
    else:
        return 0

def map_summary_form_to_dict(form, header_data):
    cts_dict = None
    if form in ['F3', 'F3A', 'F3T', 'F3N']:
        cts_dict = map_f3_to_cts(header_data)
    elif form in ['F3P', 'F3PA', 'F3PN', 'F3PT']:
        cts_dict = map_f3p_to_cts(header_data)
    elif form in ['F3X', 'F3XA', 'F3XN', 'F3XT']:
        cts_dict = map_f3x_to_cts(header_data)
    elif form in ['F5', 'F5A', 'F5N']:
        cts_dict = map_f5_to_cts(header_data)
    return cts_dict
    
def summarize_noncommittee_periodic_electronic(committee_id, force_update=True):
    committee_name = ""
    try:
        this_committee = Committee.objects.get(cmte_id=committee_id, cycle=CYCLE)
        committee_name = this_committee.cmte_name
    
    except Committee.DoesNotExist:
        print "Missing committee name"
        pass
    
    except Committee.MultipleObjectsReturned:
        print "multiple committees!! id=%s" % (committee_id)
        
        pass
        
    relevant_filings = new_filing.objects.filter(fec_id=committee_id, is_f5_quarterly=True, is_superceded=False, coverage_from_date__gte=date(2013,1,1)).order_by('coverage_from_date')
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

        last_end_date = this_filing.coverage_to_date
        form = this_filing.form_type
        header_data = this_filing.header_data

        cts_dict = map_summary_form_to_dict(form, header_data)
        #print "Form = %s cts_dict = %s" % (form, cts_dict)


        cts_dict['filing_number'] = this_filing.filing_number
        cts_dict['coverage_through_date'] = this_filing.coverage_to_date
        cts_dict['coverage_from_date'] = this_filing.coverage_from_date
        cts_dict['data_source'] = 'electronic'
        cts_dict['com_id'] = committee_id
        # only reported receipts *are* the contribs, so...
        cts_dict['tot_contrib'] = cts_dict['tot_receipts'] 
        cts_dict['com_name'] = committee_name

        for i in cts_dict:
            if cts_dict[i] == '':
                cts_dict[i] = None


        try:
            this_summary = Committee_Time_Summary.objects.get(com_id=committee_id, coverage_from_date=this_filing.coverage_from_date, coverage_through_date=this_filing.coverage_to_date)
            if force_update:

                this_summary.filing_number = this_filing.filing_number
                this_summary.tot_receipts = cts_dict.get('tot_receipts')
                this_summary.tot_contrib = cts_dict.get('tot_contrib')
                this_summary.com_name = cts_dict.get('com_name')
                this_summary.tot_disburse = cts_dict.get('tot_disburse')
                this_summary.ind_exp_mad = cts_dict.get('ind_exp_mad')
                this_summary.data_source = cts_dict.get('data_source')
                this_summary.save()

        except Committee_Time_Summary.DoesNotExist:
            cts = Committee_Time_Summary(**cts_dict)
            cts.save()






## rewrite so this can handle F5's to replace the above
def summarize_committee_periodic_electronic(committee_id, force_update=True):
    # it's a pain, but we need the committee name in this model. 
    committee_name = ""
    try:
        this_committee = Committee.objects.get(cmte_id=committee_id, cycle=CYCLE)
        committee_name = this_committee.cmte_name
    
    except Committee.DoesNotExist:
        print "Missing committee name"
        pass
    
    except Committee.MultipleObjectsReturned:
        print "multiple committees!! id=%s" % (committee_id)
        
        pass
        
    relevant_filings = new_filing.objects.filter(fec_id=committee_id, is_superceded=False, coverage_from_date__gte=date(2013,1,1), form_type__in=['F3P', 'F3PN', 'F3PA', 'F3PT', 'F3', 'F3A', 'F3N', 'F3T', 'F3X', 'F3XA', 'F3XN', 'F3XT']).order_by('coverage_from_date')
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
        
        last_end_date = this_filing.coverage_to_date
        form = this_filing.form_type
        header_data = this_filing.header_data
        
        cts_dict = map_summary_form_to_dict(form, header_data)
        #print "Form = %s cts_dict = %s" % (form, cts_dict)
        
        tot_contribs = string_to_float(cts_dict['tot_ite_contrib']) + string_to_float(cts_dict['tot_non_ite_contrib'])

        cts_dict['filing_number'] = this_filing.filing_number
        cts_dict['coverage_through_date'] = this_filing.coverage_to_date
        cts_dict['coverage_from_date'] = this_filing.coverage_from_date
        cts_dict['data_source'] = 'electronic'
        cts_dict['com_id'] = committee_id
        cts_dict['tot_contrib'] = tot_contribs 
        cts_dict['com_name'] = committee_name
        
        for i in cts_dict:
            if cts_dict[i] == '':
                cts_dict[i] = None
            
        
        try:
            this_summary = Committee_Time_Summary.objects.get(com_id=committee_id, coverage_from_date=this_filing.coverage_from_date, coverage_through_date=this_filing.coverage_to_date)
            if force_update:
                
                this_summary.filing_number = this_filing.filing_number
                this_summary.tot_receipts = cts_dict.get('tot_receipts')
                this_summary.tot_ite_contrib = cts_dict.get('tot_ite_contrib')
                this_summary.tot_non_ite_contrib = cts_dict.get('tot_non_ite_contrib')
                this_summary.tot_contrib = cts_dict.get('tot_contrib')
                this_summary.com_name = cts_dict.get('com_name')
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
            print "creating committee summary %s" % cts_dict
            cts.save()
            
## from summary_data.utils.summary_utils import summarize_committee_periodic_electronic
## summarize_committee_periodic_electronic()

def get_recent_reports(fec_id, coverage_through_date):
    if not coverage_through_date:
        coverage_through_date = this_cycle_start
        
    recent_report_list = new_filing.objects.filter(fec_id=fec_id, coverage_from_date__gte=coverage_through_date, form_type__in=['F5A', 'F5', 'F5N', 'F24', 'F24A', 'F24N', 'F6', 'F6A', 'F6N']).exclude(is_f5_quarterly=True).exclude(is_superceded=True)
    
    # for these reports only itemized contributions are reported, so tot_raised = tot_contrib = tot_ite_contrib. 
    # also , tot_spent = tot_ies, but that's tracked at the report level. Maybe do something weird for F13s on this score, I dunno. 
    summary_data = recent_report_list.aggregate(tot_contrib=Sum('tot_raised'), tot_disburse=Sum('tot_spent'), tot_ite_contrib=Sum('tot_raised'), tot_receipts=Sum('tot_raised'), coo_exp_par=Sum('tot_coordinated'), total_indy_expenditures=Sum('tot_ies'))
    
    for i in summary_data:
        if not summary_data[i]:
            summary_data[i] = 0
    
    #print "Summary data is: " + str(summary_data)
    return summary_data
    
    

# run the summary routine, generally, for any committee. Takes a committee overlay as an argument. 
def update_committee_times(committee):
    #print "Handling %s" % (committee.fec_id)

    if committee.is_paper_filer:
        summarize_committee_periodic_webk(committee.fec_id, force_update=True)
    else:
        # if they file on F5's it's different since, the same form is used for monthly and daily reports
        if committee.ctype == 'I':
            summarize_noncommittee_periodic_electronic(committee.fec_id, force_update=True)                    
        else:
            summarize_committee_periodic_electronic(committee.fec_id, force_update=True)


    ## Now that the data is summarized, update the committee_overlay. At the moment we're just looking at the two year cycle; for senate races older webk files need to be populated. Senate special elections complicte this a little; e.g. Hawaii senate race being held off cycle. 

    ## we need to log the gaps somewhere. 

    all_summaries = Committee_Time_Summary.objects.filter(com_id=committee.fec_id, coverage_from_date__gte=(date(2012,12,31))).order_by('-coverage_from_date')

    if all_summaries:
        most_recent_report = all_summaries[0]

        committee.cash_on_hand_date = most_recent_report.coverage_through_date
        
        recent_summary = get_recent_reports(committee.fec_id, most_recent_report.coverage_through_date)
        
        committee.cash_on_hand = most_recent_report.cash_on_hand_end
        committee.outstanding_loans = most_recent_report.outstanding_loans

        sums = all_summaries.aggregate(tot_contrib=Sum('tot_contrib'), tot_disburse=Sum('tot_disburse'), tot_non_ite_contrib=Sum('tot_non_ite_contrib'), tot_receipts=Sum('tot_receipts'), coo_exp_par=Sum('coo_exp_par'), total_indy_expenditures=Sum('ind_exp_mad'))
        
        for i in sums:
            if not sums[i]:
                sums[i] = 0

        committee.total_contributions = sums['tot_contrib'] + recent_summary['tot_contrib']
        committee.total_disbursements = sums['tot_disburse'] + recent_summary['tot_disburse']
        committee.total_unitemized = sums['tot_non_ite_contrib']
        committee.total_coordinated_expenditures = sums['coo_exp_par'] + recent_summary['coo_exp_par']
        committee.total_receipts = sums['tot_receipts'] + recent_summary['tot_receipts']
        committee.total_indy_expenditures = sums['total_indy_expenditures'] + recent_summary['total_indy_expenditures']
        
    
    
    else:
        # there are no committee time summaries, just use latest reports. 
        
        recent_summary = get_recent_reports(committee.fec_id, None)
        committee.total_contributions = recent_summary['tot_contrib']
        committee.total_disbursements =  recent_summary['tot_disburse']
        committee.total_coordinated_expenditures = recent_summary['coo_exp_par']
        committee.total_receipts =  recent_summary['tot_receipts']
        committee.total_indy_expenditures = recent_summary['total_indy_expenditures']
        
    
    # now check for newly set flags
    
    if not committee.has_independent_expenditures and committee.total_indy_expenditures > 0:
        committee.has_independent_expenditures = True

    if not committee.has_contributions and committee.total_contributions > 0:
        committee.has_contributions = True
    # coordinated expenditures can only be done by party committees so:
    if committee.ctype in ['Y', 'Z'] and not committee.has_coordinated_expenditures and committee.total_coordinated_expenditures > 0:
        committee.has_coordinated_expenditures = True
    committee.save()
    

def update_district_totals(district):
    # get authorized spending
    candidates = Candidate_Overlay.objects.filter(district=district)
    # expenditures is independent expenditures for or against; disbursements is spending by them.
    sums = candidates.aggregate(total_expenditures=Sum('total_expenditures'), total_receipts=Sum('total_receipts'), total_disbursements=Sum('total_disbursements'))
    for i in sums:
        if not sums[i]:
            sums[i] = 0
    
    district.candidate_raised = round(sums['total_receipts'])
    district.candidate_spending = round(sums['total_disbursements'])
    district.outside_spending = round(sums['total_expenditures'])
    
    # we're disregarding coordinated spending for now. 
    district.total_spending = round(sums['total_disbursements'] + sums['total_expenditures'])
    district.save()
    
    # todo: coordinated spending, electioneering.
