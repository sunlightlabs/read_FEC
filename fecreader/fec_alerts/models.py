from django.db import models
import re


from djorm_hstore.fields import DictionaryField
from djorm_hstore.models import HStoreManager
from parsing.read_FEC_settings import FEC_DOWNLOAD


# SHOULD GO SOMEWHERE
CURRENT_CYCLE = '2014'

form_types = [['F3X','Monthly/quarterly report'],
['F3P','Monthly/quarterly report'],
['F3L','Report of contributions bundled by lobbyist/registrants and lobbyist/registrant pacs'],
['F3','Monthly/quarterly report'],
['F99','Miscellaneous report'],
['F10','24-hour notice of expenditure from candidate\'s personal funds'],
['F13','Report of donations accepted for inaugural committee'],
['F1M','Notification of multicandidate status'],
['F1','Statement of organization'],
['F24','24/48 hr notice of independent/coordinated expenditures'],
['F2','Statement of candidacy'],
['F4','Report of receipts and disbursements - convention cmte'],
['F5','Report of independent expenditures made and contributions received'],
['F6','48-hour notice of contributions/loans received'],
['F7','Report of communication costs - corporations and membership orgs'],
['F8','Debt settlement plan'],
['F9','24-hour notice of disbursement/obligations for electioneering communications']]

class Filing_Scrape_Time(models.Model):
    run_time = models.DateTimeField(auto_now=True)
    
    
# This is just to hold newly formed committees, scraped from a special page on the press site here: http://www.fec.gov/press/press2011/new_form1dt.shtml. Form F1's don't have to be filed electronically, so the press page appears to be the best resource out there. 
class newCommittee(models.Model):
    cycle = models.CharField(max_length=4, default=CURRENT_CYCLE)
    fec_id = models.CharField(max_length=9, blank=True, unique=True)
    ctype = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    date_filed = models.DateField()
    # is it in our system? 
    has_overlay = models.NullBooleanField(null=True)


    class Meta:
        ordering = ('-date_filed', )
        

    def __unicode__(self):
        return "%s formed %s" % (self.name, self.date_filed)
    

# Class to hold new filings, whether or not they've been parsed yet. 
class new_filing(models.Model):
    fec_id = models.CharField(max_length=9)
    committee_name = models.CharField(max_length=200)
    filing_number = models.IntegerField(primary_key=True)
    form_type = models.CharField(max_length=7)
    filed_date = models.DateField(null=True, blank=True)
    coverage_from_date = models.DateField(null=True, blank=True)
    coverage_to_date = models.DateField(null=True, blank=True)
    process_time = models.DateTimeField()
    is_superpac = models.NullBooleanField()
    
    # populate from committee_overlay file. 
    committee_designation = models.CharField(max_length=1, null=True, blank=True)
    committee_type = models.CharField(max_length=1, null=True, blank=True)
    committee_slug = models.SlugField(max_length=255, null=True, blank=True)
    party = models.CharField(max_length=3, blank=True, null=True)
    
    
    
    # processing status notes
    filing_is_downloaded = models.NullBooleanField(default=False)
    header_is_processed = models.NullBooleanField(default=False)
    previous_amendments_processed = models.NullBooleanField(default=False)
    data_is_processed = models.NullBooleanField(default=False)
    
    ## New # Have the body rows in superceded filings been marked as amendments? 
    ## alter table fec_alerts_new_filing add column "body_rows_superceded" boolean;
    body_rows_superceded = models.NullBooleanField(default=False)
    
    ## summary data only available after form is parsed:
    
    # periodic reports only
    coh_start = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    coh_end = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    # Did they borrow *new* money this period ? 
    new_loans = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    
    # if applicable:
    tot_raised = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    tot_spent = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    
    # which filing types are contained? Store as a dict:
    lines_present =  DictionaryField(db_index=True, null=True)
    
    objects = HStoreManager()
    
    def get_fec_url(self):
        url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/%s/" % (self.fec_id, self.filing_number)
        return url
    
    def get_skeda_url(self):
        url = "/filings/%s/SA/" % (self.filing_number)
        return url
        
    def get_skedb_url(self):
        url = "/filings/%s/SB/" % (self.filing_number)
        return url
                    
    def get_absolute_url(self):
        url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/%s/" % (self.fec_id, self.filing_number)
        return url
            
    def fec_all_filings(self):
        url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/" % (self.fec_id)
        return url
        
    def get_form_name(self):
        report_extra = ""
        if re.search('A', self.form_type):
            report_extra=" (AMENDED)"
        if re.search('T', self.form_type):
            report_extra=" (TERMINATION REPORT)"
        for f in form_types:
            if (re.match(f[0], self.form_type)):
                return f[1] + report_extra
        return ''
    
    def FEC_url(self):
        fec_download_url = FEC_DOWNLOAD % (self.filing_number)
        return fec_download_url
            
    class Meta:
        ordering = ('-filing_number', )

        
    def __unicode__(self):
        return "%s formed %s" % (self.get_form_name(), self.filed_date)
        
        
# field names taken directly from metadata, except where noted http://www.fec.gov/finance/disclosure/metadata/metadataforcommitteesummary.shtml
# date fields are imported as they appear, but parsed into coverage_from_date and coverage_through_date. 
## Model reordered to put ids, dates at the top. 
class WebK(models.Model):
    cycle = models.CharField(max_length=4, blank=True, null=True)
    can_id = models.CharField(max_length=9, blank=True, null=True, help_text="FEC-assigned committee id")
    com_id = models.CharField(max_length=9, blank=True, null=True, help_text="FEC-assigned committee id")
    com_nam = models.CharField(max_length=200, blank=True, null=True)

    #### not in original:
    coverage_from_date = models.DateField(null=True)
    coverage_through_date = models.DateField(null=True)
    ####

    cov_sta_dat = models.CharField(max_length=200, blank=True, help_text="Coverage Start Date")
    cov_end_dat = models.CharField(max_length=200, blank=True, help_text="Coverage End Date")
    # Not imported--this can be constructed from the committee id
    lin_ima = models.CharField(max_length=127, blank=True, help_text="Coverage End Date")
    rep_typ = models.CharField(max_length=200, blank=True, null=True)
    com_typ = models.CharField(max_length=1, blank=True, null=True, help_text="committee type")
    com_des = models.CharField(max_length=1, blank=True, null=True, help_text="committee designation")
    fil_fre = models.CharField(max_length=1, blank=True, null=True, help_text="filing frequency")
    add = models.CharField(max_length=255, blank=True, null=True, help_text="address")
    cit = models.CharField(max_length=255, blank=True, null=True, help_text="city")
    sta = models.CharField(max_length=2, blank=True, null=True, help_text="state")
    zip = models.CharField(max_length=9, blank=True, null=True, help_text="zip")
    tre_nam = models.CharField(max_length=200, blank=True, null=True, help_text="treasurers name")
    fec_ele_yea = models.IntegerField(blank=True, null=True, help_text="FEC election year -- integer")
    ind_ite_con = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Individual Itemized Contribution")
    ind_uni_con = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Individual Unitemized Contribution")
    ind_con = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Total contributions from individuals ")
    ind_ref = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="contribution refunds made to individuals ")
    par_com_con = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="contributions from party committees ")
    oth_com_con = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="contributions from other committees ")
    oth_com_ref = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="contribution refunds made to other committees")
    can_con = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Contributions from the candidate ")
    tot_con = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Sum of contributions from all sources ")
    tot_con_ref = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Sum of contribution refunds made to all sources ")
    can_loa = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Sum of loans from the candidate ")
    can_loa_rep = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text=" Candidate Loan Repayment")
    oth_loa = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Sum of loans from other sources ") 
    oth_loa_rep = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Loan repayments to other sources ") 
    tot_loa = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text=" Sum of all loans") 
    tot_loa_rep = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Sum of all loan repayments ") 
    tra_fro_oth_aut_com = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Transfers received from other affiliated or authorized committees * ") 
    tra_fro_non_fed_acc = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Transfer from non Federal Account: Funds outside federal restrictions used for activities that include state or local candidates") 
    tra_fro_non_fed_lev_acc = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Transfer from non Federal Levin Account: special nonfederal funds for specific activities of state or local party committees ") 
    tot_non_fed_tra = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Total non Federal Transfer") 
    oth_rec = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Other Receipt") 
    tot_rec = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Total Receipt") 
    tot_fed_rec = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text=" Total Federal Receipt") 
    ope_exp = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Operating Expenditure") 
    sha_fed_ope_exp = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Shared Federal Operating Expenditure") 
    sha_non_fed_ope_exp = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Shared non Federal Operating Expenditure") 
    tot_ope_exp = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Total Operating Expenditure") 
    off_to_ope_exp = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Offsets to Operating Expenditure") 
    fed_sha_of_joi_act = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Federal Share of Joint Federal Election Activity") 
    non_fed_sha_of_joi_act = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Non Federal Share of Joint Federal Election Activity") 
    non_all_fed_ele_act_par = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Non Allocated Federal Election Activity (Party only)") 
    tot_fed_ele_act = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text=" 	Total Federal Election Activity") 
    fed_can_com_con = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Federal Candidate Committee Contribution: contributions to federal campaigns or other federal committees (e.g. PACs or parties) ") 
    fed_can_con_ref = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Federal Candidate Contribution Refund") 
    ind_exp_mad = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Independent Expenditures Made") 
    coo_exp_par = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Coordinated Expenditure (Party only)") 
    loa_mad = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Loan Made") 
    loa_rep_rec = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Loan Repayments Received") 
    tra_to_oth_aut_com = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Transfer to Other Authorized Committee") 
    fun_dis = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Fundraising Disbursement") 
    off_to_fun_exp_pre = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Offsets to Fundraising Expenses (Presidential only)") 
    exe_leg_acc_dis_pre = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Exempt Legal/Accounting Disbursement (Presidential only)") 
    off_to_leg_acc_exp_pre = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Offsets to Legal/Accounting Expenses (Presidential only)") 
    tot_off_to_ope_exp = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Total Offsets to Operating Expenditure")
    oth_dis = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Other Disbursemen")
    tot_fed_dis = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Total Federal Disbursement")
    tot_dis = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Total Disbursement")
    net_con = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text=" Net Contribution")
    net_ope_exp = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Net Operating Expenditure")
    cas_on_han_beg_of_per = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Cash on Hand Beginning of Period")
    cas_on_han_clo_of_per = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Cash on Hand Closing of Period")
    deb_owe_by_com = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Debt Owed by Committee")
    deb_owe_to_com = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Debt Owed to Committee")
    pol_par_com_ref = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Political Party Committee Refund")

    cas_on_han_beg_of_yea = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Cash on Hand Beginning of Year")
    cas_on_han_clo_of_yea = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Cash on Hand Closing of Year")
    exp_sub_to_lim_pri_yea_pre = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Expenditures Subject to Limit - Prior Year (Presidential only)")
    exp_sub_lim = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Expenditures Subject to Limit")
    fed_fun = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Federal Funds")

    ite_con_exp_con_com = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Itemized Convention Expenditure (Convention Committee only)")
    ite_oth_dis = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Itemized Other Disbursement")
    ite_oth_inc = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Itemized Other Income")
    ite_oth_ref_or_reb = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Itemized Other Refunds or Rebates")
    ite_ref_or_reb = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Itemized Refunds or Rebates")
    oth_fed_ope_exp = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Other Federal Operating Expenditures")
    sub_con_exp = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Subtotal Convention Expenses")
    sub_oth_ref_or_reb = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Subtotal Other Refunds or Rebates")
    sub_ref_or_reb = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Subtotal Refunds or Rebates")
    tot_com_cos = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Total Communication Cost")
    tot_exp_sub_to_lim_pre = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Total Expenditures Subject to Limit (Presidential only)")
    uni_con_exp = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Unitemized Convention Expenses")
    uni_oth_dis = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Unitemized Other Disbursements")
    uni_oth_inc = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text=" Unitemized Other Income")
    uni_oth_ref_or_reb = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Unitemized other Refunds or Rebates")
    uni_ref_or_reb = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, help_text="Unitemized Refunds or Rebates")
    org_tp = models.CharField(max_length=1, null=True, help_text="Organization Type")
