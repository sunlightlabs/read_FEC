"""
* We have to drop the primary key indexes that django creates and create a different one with specific settings--see formdata/sql/<model>.sql for details. 

"""



from django.db import models
from django.utils.text import slugify

from djorm_hstore.fields import DictionaryField
from djorm_hstore.models import HStoreManager

from summary_data.models import District, Candidate_Overlay
from api.nulls_last_queryset import NullsLastManager


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
    candidate_id_checked = models.CharField(max_length=9, blank=True, null=True, help_text="The FEC id of the candidate targeted by this independent expenditure. This is added whenever possible from expenditures that are missing it.")
    district_checked = models.ForeignKey(District, null=True)
    candidate_party_checked = models.CharField(max_length=3, blank=True, null=True, help_text="The candidate's party. This is added whenever possible from expenditures that are missing it.")
    candidate_name_checked = models.CharField(max_length=255, blank=True, null=True, help_text="The candidate's name. This is added whenever possible from expenditures that are missing it.")
    candidate_office_checked = models.CharField(max_length=255, blank=True, null=True, help_text="The candidate's office. This is added whenever possible from expenditures that are missing it.")
    candidate_state_checked = models.CharField(max_length=2, blank=True, null=True, help_text="The state the candidate is running in. This is absent from presidential candidates. This is added whenever possible from expenditures that are missing it.")
    candidate_district_checked = models.CharField(max_length=2, blank=True, null=True, help_text="The candidate's district, if applicable. This is added whenever possible from expenditures that are missing it.")
    support_oppose_checked = models.CharField(max_length=1, blank=True, null=True, help_text="Whether the expenditure supports (S) or opposes (O) the candidate.")
    committee_name = models.CharField(max_length=255, blank=True, null=True, help_text="The name of the committee making the expenditure")
    committee_slug = models.CharField(max_length=255, blank=True, null=True)
    
    effective_date = models.DateField(null=True, help_text="What date should we use? Through version 8.0 of FECfile, there was only an 'expenditure date', but beginning with v8.1 there were two dates--a dissemination date and an expenditure date. For v8.1 use the dissemination date; for earlier version use the expenditure date.")
    

    # from the model
    form_type = models.CharField(max_length=8, blank=True)
    filer_committee_id_number = models.CharField(max_length=9, blank=True, null=True)
    transaction_id  = models.CharField(max_length=20, blank=True, null=True, help_text="The transaction id from the original filing. These ids are unique per report, not necessarily per cycle.")
    back_reference_tran_id_number = models.CharField(max_length=20, blank=True, null=True)
    back_reference_sched_name  = models.CharField(max_length=8, blank=True, null=True)
    entity_type =  models.CharField(max_length=3, blank=True, null=True, help_text='[CAN|CCM|COM|IND|ORG|PAC|PTY]')
    
    payee_name = models.CharField(max_length=100, blank=True, null=True, help_text="deprecated")
    payee_organization_name = models.CharField(max_length=200, blank=True, null=True, help_text="The name of the organization being paid")
    payee_last_name = models.CharField(max_length=30, blank=True, null=True)
    payee_first_name = models.CharField(max_length=20, blank=True, null=True)
    payee_middle_name = models.CharField(max_length=20, blank=True, null=True)
    payee_prefix = models.CharField(max_length=10, blank=True, null=True)
    payee_suffix = models.CharField(max_length=10, blank=True, null=True)
    payee_street_1 = models.CharField(max_length=34, blank=True, null=True, help_text="The street address of the payee")
    payee_street_2 = models.CharField(max_length=34, blank=True, null=True, help_text="The street address of the payee -- second part, if needed.")
    payee_city = models.CharField(max_length=30, blank=True, null=True, help_text="The payee's city")
    payee_state = models.CharField(max_length=2, blank=True, null=True, help_text="Payee state")
    payee_zip = models.CharField(max_length=9, blank=True, null=True, help_text="Payee ZIP code")
    election_code = models.CharField(max_length=5, blank=True, null=True, help_text="The code describing the election")
    election_other_description = models.CharField(max_length=20, blank=True, null=True, help_text="Any additional description of the election")
    expenditure_date = models.CharField(max_length=8, blank=True, null=True)
    expenditure_date_formatted = models.DateField(null=True, help_text="The date of the expenditure")
    dissemination_date = models.CharField(max_length=8, blank=True, null=True, help_text="The dissemination date, only in v8.1 and higher.")
    dissemination_date_formatted = models.DateField(null=True, help_text="The dissemination date, only in v8.1 and higher.")
    
    
    expenditure_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, help_text="The expenditure amount")
    calendar_y_t_d_per_election_office = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    expenditure_purpose_code = models.CharField(max_length=3, blank=True, null=True, help_text="The filer-entered code of the expenditure. This isn't required.")
    expenditure_purpose_descrip = models.CharField(max_length=100, blank=True, null=True, help_text="The filer-described purpose of the expenditure")
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
    memo_code = models.CharField(max_length=1, blank=True, null=True, help_text="This is an X for lines that are subitemizations")
    memo_text_description = models.CharField(max_length=100, blank=True, null=True, help_text="A text description of unique circumstances surrounding this expenditure.")
    
    # make nulls sort last
    objects = models.Manager()
    nulls_last_objects = NullsLastManager()

    def payee_name_simplified(self):
        if self.payee_organization_name:
           return self.payee_organization_name
      
        return "%s, %s %s %s" % (self.payee_last_name, self.payee_first_name, self.payee_middle_name or "", self.payee_suffix or "")
    
    def support_oppose(self):
        # fall back on original code if new one isn't processed.
        if self.support_oppose_checked:
            if self.support_oppose_checked.upper() == 'S':
                return '<div class="label-support">Support</div>'
            elif self.support_oppose_checked.upper() == 'O':
                return '<div class="label-oppose">Oppose</div>'
            
        elif self.support_oppose_code:
            if self.support_oppose_code.upper() == 'S':
                return '<div class="label-support">Support</div>'
            elif self.support_oppose_code.upper() == 'O':
                return '<div class="label-oppose">Oppose</div>'            
            
        return ""
    
    def candidate_name_raw(self):
        if self.candidate_name_checked:
            return self.candidate_name_checked
        else:
            return "%s, %s %s" % (self.candidate_last_name, self.candidate_first_name, self.candidate_middle_name or "")
    
    def get_candidate_url(self):
        if self.candidate_id_checked:
            return "/candidate/%s/%s/" % (slugify(unicode(self.candidate_name_raw())), self.candidate_id_checked)
        elif self.candidate_id_number:
            return "/candidate/%s/%s/" % (slugify(unicode(self.candidate_name_raw())), self.candidate_id_number)
        else:
            return None
            
    def get_committee_url(self):
        return "/committee/%s/%s/" % (self.committee_slug, self.filer_committee_id_number)
    
    def short_office(self):
            
        if self.candidate_office_checked == 'S':
            return '%s (Sen.)' % (self.candidate_state_checked)
        elif self.candidate_office_checked =='H':
            return '%s-%s' % (self.candidate_state_checked, self.candidate_district_checked)
        else:
            return ""
            
    def get_absolute_url(self):
        return "/filings/%s/#%s" % (self.filing_number, self.transaction_id)
        
    def supporting_opposing(self):
        support = 'naming'
        if self.support_oppose_code == 'S':
            support='supporting'
        elif self.support_oppose_code == 'O':
            support = 'opposing'    
        return support

    def get_race_url(self):
        if self.candidate_office_checked == 'H':
            return "/race/%s/%s/%s/%s/" % ('2014', self.candidate_office_checked, self.candidate_state_checked, self.candidate_district_checked)
        elif self.candidate_office_checked == 'S' and self.district_checked:
            return "/race_id/%s/" % (self.district_checked.pk)
            
        elif self.candidate_office == 'H':
            return "/race/%s/%s/%s/%s/" % ('2014', self.candidate_office, self.candidate_state, self.candidate_district)
            
            
        elif self.candidate_office == 'S' and self.district_checked:
            return "/race_id/%s/" % (self.district_checked.pk)
        
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

