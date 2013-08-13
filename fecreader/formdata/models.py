"""
* We have to drop the primary key indexes that django creates and create a different one with specific settings--see formdata/sql/<model>.sql for details. 

"""



from django.db import models

from djorm_hstore.fields import DictionaryField
from djorm_hstore.models import HStoreManager

from summary_data.models import District, Candidate_Overlay


# This is a flag for when we need to update summary stats on a committee. If we touch a committee, mark it here. Remove it when fixed. Hourly(ish) scripts will do the recalculating...
class Committee_Changed(models.Model):
    committee_id=models.CharField(max_length=9, blank=True)
    time = models.DateTimeField(auto_now=True)
    
# Because the entry process for data rows is done by non-django processes, we need to track when it's done. Also mark when it starts, so that if it fails half way through we have some db record of it (and hence don't have to wade through log files)
# class Filing_Data_Entry_Status(models.Model):
#     filing_number=models.IntegerField(unique=True)
#     entry_begun = models.BooleanField()
#     entry_complete = models.BooleanField()
#     is_error = models.BooleanField(help_text="If there's an error, flag it here--however, any file where entry has begun and not finished some amount of time later can probably be considered to be in error")
#     error_text = models.TextField("Text of first DB error -- we give up on entry after the first error.")
#     last_update_time = models.DateTimeField(auto_now=True)
#     # which filing types are contained? Store as a dict:
#     lines_present =  DictionaryField(db_index=True, null=True)
#     objects = HStoreManager()

class Filing_Header(models.Model):
    raw_filer_id=models.CharField(max_length=9, blank=True)
#    filer = models.ForeignKey(Committee_Overlay, null=True)
    form=models.CharField(max_length=7)
    # Is filing_number gonna be unique within a cycle? 
    filing_number=models.IntegerField(unique=True)
    version=models.CharField(max_length=7)
    
    coverage_from_date = models.DateField(null=True)
    coverage_through_date = models.DateField(null=True)
    
    # does this supercede another an filing?
    is_amendment=models.BooleanField()
    # if so, what's the original?
    amends_filing=models.IntegerField(null=True, blank=True)
    amendment_number = models.IntegerField(null=True, blank=True)
    
    # Is this filing superceded by another filing, either a later amendment, or a periodic filing.
    is_superceded=models.BooleanField(default=False)
    # which filing is this one superceded by? 
    amended_by=models.IntegerField(null=True, blank=True)
    
    # Is this a 24- or 48- hour notice that is now covered by a periodic (monthly/quarterly) filing, and if so, is ignorable ? 
    covered_by_periodic_filing=models.BooleanField(default=False)
    covered_by=models.IntegerField(null=True, blank=True)
    
    # When did the filing come in? 
    filing_time = models.DateTimeField(auto_now=False, null=True)
    # Is this an exact time, or is it a day estimated from the zip file directories ? 
    filing_time_is_exact = models.BooleanField()
    
    # Shortcut to store whether the files' been totally processed; helpful in tracking down filings where entry failed and they are now half done. 
    entry_complete = models.BooleanField(default=False)

    # store the actual header data as an hstore here:
    header_data = DictionaryField(db_index=False)
    
    # which filing types are contained? Store as a dict:
    lines_present =  DictionaryField(db_index=True, null=True)
    
    objects = HStoreManager()
    
    def __unicode__(self):
        return str(self.filing_number)
    

        
# field sizes are based on v8.0 specs, generally
class SkedA(models.Model):
    # additional fields 
    header_id = models.IntegerField()
    filing_number = models.IntegerField()
    superceded_by_amendment = models.BooleanField(default=False)
    
    # from the model
    form_type = models.CharField(max_length=8, blank=True)
    filer_committee_id_number = models.CharField(max_length=9, blank=True, null=True)
    transaction_id  = models.CharField(max_length=20, blank=True, null=True)
    back_reference_tran_id_number = models.CharField(max_length=20, blank=True, null=True)
    back_reference_sched_name  = models.CharField(max_length=8, blank=True, null=True)
    entity_type =  models.CharField(max_length=3, blank=True, null=True, help_text='[CAN|CCM|COM|IND|ORG|PAC|PTY]')
    # Should be wrapped to newer version? 
    contributor_name = models.CharField(max_length=200, blank=True, null=True, help_text="deprecated as a field since v5.3")
    contributor_organization_name = models.CharField(max_length=200, blank=True, null=True)
    contributor_last_name  = models.CharField(max_length=30, blank=True, null=True)
    contributor_first_name = models.CharField(max_length=20, blank=True, null=True)
    contributor_middle_name = models.CharField(max_length=20, blank=True, null=True)
    contributor_prefix= models.CharField(max_length=10, blank=True, null=True)
    contributor_suffix = models.CharField(max_length=10, blank=True, null=True)
    contributor_street_1 = models.CharField(max_length=34, blank=True, null=True)
    contributor_street_2 = models.CharField(max_length=34, blank=True, null=True)
    contributor_city = models.CharField(max_length=30, blank=True, null=True)
    contributor_state = models.CharField(max_length=2, blank=True, null=True)
    contributor_zip = models.CharField(max_length=9, blank=True, null=True)
    election_code = models.CharField(max_length=5, blank=True, null=True)
    election_other_description = models.CharField(max_length=20, blank=True, null=True, help_text="required if election code starts with 'O' for other")
    contribution_date = models.CharField(max_length=8, blank=True, null=True, help_text="exactly as it appears")
    contribution_date_formatted = models.DateField(null=True, help_text="Populated from parsing raw field")
    contribution_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    contribution_aggregate = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    contribution_purpose_code = models.CharField(max_length=3, blank=True, null=True, help_text="deprecated")
    contribution_purpose_descrip = models.CharField(max_length=100, blank=True, null=True)
#    increased_limit_code = models.CharField(max_length=10, blank=True, null=True, help_text="deprecated after 6.4 or so")
    contributor_employer = models.CharField(max_length=38, blank=True, null=True)
    contributor_occupation = models.CharField(max_length=38, blank=True, null=True)
    donor_committee_fec_id = models.CharField(max_length=9, blank=True, null=True)
    donor_committee_name = models.CharField(max_length=200, blank=True, null=True)
    donor_candidate_fec_id = models.CharField(max_length=9, blank=True, null=True)
    # should be updated to new, if possible... 
    donor_candidate_name = models.CharField(max_length=200, blank=True, null=True, help_text="deprecated")
    donor_candidate_last_name = models.CharField(max_length=30, blank=True, null=True)
    donor_candidate_first_name = models.CharField(max_length=20, blank=True, null=True)
    donor_candidate_middle_name = models.CharField(max_length=20, blank=True, null=True)
    donor_candidate_prefix  = models.CharField(max_length=10, blank=True, null=True)
    donor_candidate_suffix = models.CharField(max_length=10, blank=True, null=True)
    donor_candidate_office = models.CharField(max_length=1, blank=True, null=True)
    donor_candidate_state = models.CharField(max_length=2, blank=True, null=True)
    donor_candidate_district = models.CharField(max_length=2, blank=True, null=True)
    conduit_name = models.CharField(max_length=200, blank=True, null=True)
    conduit_street1 = models.CharField(max_length=34, blank=True, null=True)
    conduit_street2 = models.CharField(max_length=34, blank=True, null=True)
    conduit_city = models.CharField(max_length=30, blank=True, null=True)
    conduit_state = models.CharField(max_length=2, blank=True, null=True)
    conduit_zip = models.CharField(max_length=9, blank=True, null=True)
    memo_code = models.CharField(max_length=1, blank=True, null=True)
    memo_text_description = models.CharField(max_length=100, blank=True, null=True)
    reference_code = models.CharField(max_length=9, blank=True, null=True)
    
    def donor_name(self):
        if self.contributor_organization_name:
           return self.contributor_organization_name
          
        return "%s, %s %s %s" % (self.contributor_last_name, self.contributor_first_name, self.contributor_middle_name or "", self.contributor_suffix or "")
        

class SkedB(models.Model):
    # additional fields 
    header_id = models.IntegerField()
    filing_number = models.IntegerField()
    superceded_by_amendment = models.BooleanField(default=False)

    # from the field
    form_type = models.CharField(max_length=8, blank=True)
    filer_committee_id_number = models.CharField(max_length=9, blank=True, null=True)
    transaction_id  = models.CharField(max_length=20, blank=True, null=True)
    back_reference_tran_id_number = models.CharField(max_length=20, blank=True, null=True)
    back_reference_sched_name  = models.CharField(max_length=8, blank=True, null=True)
    entity_type =  models.CharField(max_length=3, blank=True, null=True, help_text='[CAN|CCM|COM|IND|ORG|PAC|PTY]')
    payee_name = models.CharField(max_length=100, blank=True, null=True, help_text="deprecated")
    payee_organization_name = models.CharField(max_length=200, blank=True, null=True)
    payee_last_name = models.CharField(max_length=30, blank=True, null=True)
    payee_first_name = models.CharField(max_length=20, blank=True, null=True)
    payee_middle_name  = models.CharField(max_length=20, blank=True, null=True)
    payee_prefix = models.CharField(max_length=10, blank=True, null=True)
    payee_suffix = models.CharField(max_length=10, blank=True, null=True)
    payee_street_1 = models.CharField(max_length=34, blank=True, null=True)
    payee_street_2 = models.CharField(max_length=34, blank=True, null=True)
    payee_city = models.CharField(max_length=30, blank=True, null=True)
    payee_state = models.CharField(max_length=2, blank=True, null=True)
    payee_zip = models.CharField(max_length=9, blank=True, null=True)
    election_code = models.CharField(max_length=5, blank=True, null=True)
    election_other_description = models.CharField(max_length=20, blank=True, null=True,  help_text="required if election code starts with 'O' for other")
    expenditure_date = models.CharField(max_length=8, blank=True, null=True, help_text="exactly as it appears")
    expenditure_date_formatted = models.DateField(null=True, help_text="Populated from parsing raw field")
    expenditure_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    semi_annual_refunded_bundled_amt = models.DecimalField(max_digits=14, decimal_places=2, null=True, help_text="Used for F3L only")
    expenditure_purpose_code = models.CharField(max_length=3, blank=True, null=True, help_text="deprecated")
    expenditure_purpose_descrip = models.CharField(max_length=100, blank=True, null=True)
    category_code = models.CharField(max_length=3, blank=True, null=True)
    beneficiary_committee_fec_id = models.CharField(max_length=9, blank=True, null=True)
    beneficiary_committee_name = models.CharField(max_length=200, blank=True, null=True)
    beneficiary_candidate_fec_id = models.CharField(max_length=9, blank=True, null=True)
    beneficiary_candidate_name = models.CharField(max_length=100, blank=True, null=True, help_text="deprecated")
    beneficiary_candidate_last_name = models.CharField(max_length=30, blank=True, null=True)
    beneficiary_candidate_first_name = models.CharField(max_length=20, blank=True, null=True)
    beneficiary_candidate_middle_name = models.CharField(max_length=20, blank=True, null=True)
    beneficiary_candidate_prefix = models.CharField(max_length=10, blank=True, null=True)
    beneficiary_candidate_suffix = models.CharField(max_length=10, blank=True, null=True)
    beneficiary_candidate_office = models.CharField(max_length=1, blank=True, null=True)
    beneficiary_candidate_state = models.CharField(max_length=2, blank=True, null=True)
    beneficiary_candidate_district = models.CharField(max_length=2, blank=True, null=True)
    conduit_name = models.CharField(max_length=200, blank=True, null=True)
    conduit_street_1 = models.CharField(max_length=34, blank=True, null=True)
    conduit_street_2 = models.CharField(max_length=34, blank=True, null=True)
    conduit_city  = models.CharField(max_length=30, blank=True, null=True)
    conduit_state = models.CharField(max_length=2, blank=True, null=True)
    conduit_zip = models.CharField(max_length=9, blank=True, null=True)
    memo_code = models.CharField(max_length=1, blank=True, null=True)
    memo_text_description = models.CharField(max_length=100, blank=True, null=True)
    
    #reference_to_si_or_sl_system_code_that_identifies_the_account
    ref_to_sys_code_ids_acct = models.CharField(max_length=9, blank=True, null=True)
    refund_or_disposal_of_excess = models.CharField(max_length=20, blank=True, null=True, help_text="deprecated")
    communication_date = models.CharField(max_length=9, blank=True, null=True, help_text="deprecated")


    def payee_name_simplified(self):
        if self.payee_organization_name:
           return self.payee_organization_name
      
        return "%s, %s %s %s" % (self.payee_last_name, self.payee_first_name, self.payee_middle_name or "", self.payee_suffix or "")

class SkedE(models.Model):
    # additional fields 
    header_id = models.IntegerField()
    filing_number = models.IntegerField()
    # can be superceded by amendment or by later filing
    superceded_by_amendment = models.BooleanField(default=False)
    
    ## Data added fields. Party isn't part of the original data, so...
    candidate_checked = models.ForeignKey(Candidate_Overlay, null=True)
    candidate_id_checked = models.CharField(max_length=9, blank=True, null=True)
    district_checked = models.ForeignKey(District, null=True)
    candidate_party_checked = models.CharField(max_length=3, blank=True, null=True)
    candidate_name_checked = models.CharField(max_length=255, blank=True, null=True)
    candidate_office_checked = models.CharField(max_length=255, blank=True, null=True)
    candidate_state_checked = models.CharField(max_length=2, blank=True, null=True)
    candidate_district_checked = models.CharField(max_length=2, blank=True, null=True)
    support_oppose_checked = models.CharField(max_length=1, blank=True, null=True)

    # from the model
    form_type = models.CharField(max_length=8, blank=True)
    filer_committee_id_number = models.CharField(max_length=9, blank=True, null=True)
    transaction_id  = models.CharField(max_length=20, blank=True, null=True)
    back_reference_tran_id_number = models.CharField(max_length=20, blank=True, null=True)
    back_reference_sched_name  = models.CharField(max_length=8, blank=True, null=True)
    entity_type =  models.CharField(max_length=3, blank=True, null=True, help_text='[CAN|CCM|COM|IND|ORG|PAC|PTY]')
    
    payee_name = models.CharField(max_length=100, blank=True, null=True, help_text="deprecated")
    payee_organization_name = models.CharField(max_length=200, blank=True, null=True)
    payee_last_name = models.CharField(max_length=30, blank=True, null=True)
    payee_first_name = models.CharField(max_length=20, blank=True, null=True)
    payee_middle_name = models.CharField(max_length=20, blank=True, null=True)
    payee_prefix = models.CharField(max_length=10, blank=True, null=True)
    payee_suffix = models.CharField(max_length=10, blank=True, null=True)
    payee_street_1 = models.CharField(max_length=34, blank=True, null=True)
    payee_street_2 = models.CharField(max_length=34, blank=True, null=True)
    payee_city = models.CharField(max_length=30, blank=True, null=True)
    payee_state = models.CharField(max_length=2, blank=True, null=True)
    payee_zip = models.CharField(max_length=9, blank=True, null=True)
    election_code = models.CharField(max_length=5, blank=True, null=True)
    election_other_description = models.CharField(max_length=20, blank=True, null=True)
    expenditure_date = models.CharField(max_length=8, blank=True, null=True)
    expenditure_date_formatted = models.DateField(null=True, help_text="Populated from parsing raw field")
    expenditure_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    calendar_y_t_d_per_election_office = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    expenditure_purpose_code = models.CharField(max_length=3, blank=True, null=True, help_text="deprecated")
    expenditure_purpose_descrip = models.CharField(max_length=100, blank=True, null=True)
    category_code = models.CharField(max_length=3, blank=True, null=True)
    payee_cmtte_fec_id_number = models.CharField(max_length=9, blank=True, null=True)
    support_oppose_code = models.CharField(max_length=1, blank=True, null=True)
    candidate_id_number = models.CharField(max_length=9, blank=True, null=True)
    candidate_name = models.CharField(max_length=100, blank=True, null=True, help_text="deprecated")
    candidate_last_name  = models.CharField(max_length=30, blank=True, null=True)
    candidate_first_name = models.CharField(max_length=20, blank=True, null=True)
    candidate_middle_name = models.CharField(max_length=20, blank=True, null=True)
    candidate_prefix = models.CharField(max_length=10, blank=True, null=True)
    candidate_suffix = models.CharField(max_length=10, blank=True, null=True)
    candidate_office = models.CharField(max_length=1, blank=True, null=True)
    candidate_state = models.CharField(max_length=2, blank=True, null=True)
    candidate_district = models.CharField(max_length=2, blank=True, null=True)
    completing_last_name = models.CharField(max_length=30, blank=True, null=True)
    completing_first_name = models.CharField(max_length=20, blank=True, null=True)
    completing_middle_name = models.CharField(max_length=20, blank=True, null=True)
    completing_prefix = models.CharField(max_length=10, blank=True, null=True)
    completing_suffix = models.CharField(max_length=10, blank=True, null=True)
    date_signed = models.CharField(max_length=8, blank=True, null=True)
    date_signed_formatted = models.DateField(null=True, help_text="Populated from parsing raw field")
    memo_code = models.CharField(max_length=1, blank=True, null=True)
    memo_text_description = models.CharField(max_length=100, blank=True, null=True)


    def payee_name_simplified(self):
        if self.payee_organization_name:
           return self.payee_organization_name
      
        return "%s, %s %s %s" % (self.payee_last_name, self.payee_first_name, self.payee_middle_name or "", self.payee_suffix or "")
    
    def support_oppose(self):
        if self.support_oppose_checked.upper() == 'S':
            return "Support"
        elif self.support_oppose_checked.upper() == 'O':
            return "Oppose"
        return ""
    
    def candidate_name_raw(self):
        return "%s, %s %s" % (self.candidate_last_name, self.candidate_first_name, self.candidate_middle_name or "")
    
        
class OtherLine(models.Model):
    # additional fields 
    header_id = models.IntegerField()
    filing_number = models.IntegerField()
    superceded_by_amendment = models.BooleanField(default=False)
    
    # Standardized name of the parser we use to process it.
    form_parser = models.CharField(max_length=6, blank=True)

    # from the model
    form_type = models.CharField(max_length=8, blank=True)
    filer_committee_id_number = models.CharField(max_length=9, blank=True, null=True)
    transaction_id  = models.CharField(max_length=20, blank=True, null=True)
    
    # Store all other line data as a dict:
    line_data =  DictionaryField(db_index=False, null=True)
    objects = HStoreManager()
    
# the webk summary file is now being served from the data catalog page--see here:
# http://www.fec.gov/data/CommitteeSummary.do?format=html&election_yr=2014

