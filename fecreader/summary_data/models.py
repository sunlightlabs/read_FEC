import datetime

from django.db import models

#from django_localflavor_us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.us_states import STATE_CHOICES

from ftpdata.models import Candidate
from legislators.models import Legislator

STATE_CHOICES_DICT = dict(STATE_CHOICES)

ELECTION_TYPE_CHOICES = (('G', 'General'), ('P', 'Primary'), ('R', 'Runoff'), ('SP', 'Special Primary'), ('SR', 'Special Runoff'), ('SG', 'Special General'), ('O', 'Other'))

type_hash={'C': 'Communication Cost',
          'D': 'Delegate',
          'E': 'Electioneering Communication',
          'H': 'House',
          'I': 'Not a Committee',
          'N': 'Non-Party, Non-Qualified',
          'O': 'Super PAC',
          'P': 'Presidential',
          'Q': 'Qualified, Non-Party',
          'S': 'Senate',
          'U': 'Single candidate independent expenditure',
          'V': 'PAC with Non-Contribution Account - Nonqualified',
          'W': 'PAC with Non-Contribution Account - Qualified',
          'X': 'Non-Qualified Party',
          'Y': 'Qualified Party',
          'Z': 'National Party Organization',
          }

committee_designation_hash = {'A':'Authorized by Candidate',
                            'J': 'Joint Fund Raiser',
                            'P': 'Principal Committee of Candidate',
                            'U': 'Unauthorized',
                            'B': 'Lobbyist/Registrant PAC',
                            'D': 'Leadership PAC'
                            }

# There are many different data sets that are updated. Keep track of them here.
# options are "scrape_electronic_filings", "scrape_new_committees",...
class Update_Time(models.Model):
  key = models.SlugField()
  update_time = models.DateTimeField()

  def save(self, *args, **kwargs):
      ''' On save, update timestamps '''
      self.update_time = datetime.datetime.today()
      super(Update_Time, self).save(*args, **kwargs)

## The US congress repo doesn't do a good job handling fec ids, so distill what we need into this model.
## Incumbents are populated from US Congress, and challengers from fec master file. The determination of 
## who is and who isn't a challenger is solely based on US congress, though this can be flipped through the admin. 
class Incumbent(models.Model):
  is_incumbent = models.BooleanField(default=False,help_text="Are they an incumbent? If not, they are a challenger")
  cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
  name = models.CharField(max_length=255, blank=True, null=True, help_text="incumbent name")
  fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="FEC candidate id")
  state = models.CharField(max_length=2, blank=True, null=True, help_text="US for president")
  office = models.CharField(max_length=1, null=True,
                            choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                            )
  office_district = models.CharField(max_length=2, blank=True, null=True, help_text="'00' for at-large congress; null for senate, president")
  
  def __unicode__(self):
      return self.name

class Committee_Overlay(models.Model):


  cycle = models.CharField(max_length=4)
  term_class = models.IntegerField(blank=True, null=True, help_text="1,2 or 3. Pulled from US Congress repo. Only applies to PCC of senators.")
  is_paper_filer = models.NullBooleanField(null=True, default=False, help_text="True for most senate committees, also NRSC/DSCC, some others.")    
  

  # direct from the raw fec table
  name = models.CharField(max_length=255)
  display_name = models.CharField(max_length=255, null=True)
  fec_id = models.CharField(max_length=9, blank=True)
  slug = models.SlugField(max_length=100)
  party = models.CharField(max_length=3, blank=True)
  treasurer = models.CharField(max_length=200, blank=True, null=True)
  street_1 = models.CharField(max_length=34, blank=True, null=True)
  street_2 = models.CharField(max_length=34, blank=True, null=True)
  city =models.CharField(max_length=30, blank=True, null=True)
  zip_code = models.CharField(max_length=9, blank=True, null=True)
  state = models.CharField(max_length=2, blank=True, null=True, help_text='the state where the pac mailing address is')
  connected_org_name=models.CharField(max_length=200, blank=True)
  filing_frequency = models.CharField(max_length=1, blank=True)

  candidate_id = models.CharField(max_length=9,blank=True)
  candidate_office = models.CharField(max_length=1, blank=True)    


  has_contributions = models.NullBooleanField(null=True, default=False)
  # total receipts
  total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True)
  total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True)
  

  # total unitemized receipts
  total_unitemized = models.DecimalField(max_digits=19, decimal_places=2, null=True)

  
  # independent expenditures
  has_independent_expenditures = models.NullBooleanField(null=True, default=False)
  total_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
  ie_support_dems = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
  ie_oppose_dems = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
  ie_support_reps = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
  ie_oppose_reps = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
  total_presidential_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)

  # Typically only party committees make coordinated expenditures
  has_coordinated_expenditures = models.NullBooleanField(null=True, default=False)
  total_coordinated_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)

  has_electioneering = models.NullBooleanField(null=True, default=False)
  total_electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True)

  cash_on_hand = models.DecimalField(max_digits=19, decimal_places=2, null=True)
  cash_on_hand_date = models.DateField(null=True)

  # what kinda pac is it? 
  is_superpac = models.NullBooleanField(null=True, default=False)    
  is_hybrid = models.NullBooleanField(null=True, default=False)  
  is_noncommittee = models.NullBooleanField(null=True, default=False)


  org_status = models.CharField(max_length=31,
          choices=(('501(c)(4)', '501(c)(4)'),
                   ('501(c)(5)', '501(c)(5)'),
                   ('501(c)(6)', '501(c)(6)'),
                   ('527', '527'),
                   ('Private business', 'Private business'),
                   ('Public business', 'Public business'),
                   ('Individual', 'individual'),
          ),
          blank=True, null=True, help_text="We're only tracking these for non-committees")

  # what's their orientation
  political_orientation = models.CharField(max_length=1,null=True, choices=[
                          ('R', 'backs Republicans'),
                          ('D', 'backs Democrats'),
                          ('U', 'unknown'),
                          ('C', 'opposes incumbents--supports Tea Party'),
                        ])
  political_orientation_verified = models.BooleanField(default=False, help_text="Check this box if the political orientation is correct")

  designation = models.CharField(max_length=1,
                                    blank=False,
                                    null=True,
                                    choices=[('A', 'Authorized by Candidate'),
                                             ('J', 'Joint Fund Raiser'),
                                             ('P', 'Principal Committee of Candidate'),
                                             ('U', 'Unauthorized'),
                                             ('B', 'Lobbyist/Registrant PAC'),
                                             ('D', 'Leadership PAC')]
  )

  ctype = models.CharField(max_length=1,
                          blank=False,
                          null=True,
                          choices=[('C', 'Communication Cost'),
                                     ('D', 'Delegate'),
                                     ('E', 'Electioneering Communication'),
                                     ('H', 'House'),
                                     ('I', 'Independent Expenditure (Not a Committee'),
                                     ('N', 'Non-Party, Non-Qualified'),
                                     ('O', 'Super PAC'),
                                     ('P', 'Presidential'),
                                     ('Q', 'Qualified, Non-Party'),
                                     ('S', 'Senate'),
                                     ('U', 'Single candidate independent expenditure'),
                                     ('V', 'PAC with Non-Contribution Account - Nonqualified'),
                                     ('W', 'PAC with Non-Contribution Account - Qualified'),
                                     ('X', 'Non-Qualified Party'),
                                     ('Y', 'Qualified Party'),
                                     ('Z', 'National Party Organization') ])  


  class Meta:
      unique_together = (("cycle", "fec_id"),)
      ordering = ('-total_indy_expenditures', )

  def get_absolute_url(self):  
      return ("/outside-spenders/2014/committee/%s/%s/" % (self.slug, self.fec_id))

  def is_not_a_committee(self):
      if self.committee_master_record.ctype=='I':
          return True
      return False

  def neg_percent(self):
      if self.total_indy_expenditures == 0:
          return 0
      else:
          return 100*(self.ie_oppose_reps + self.ie_oppose_dems ) / self.total_indy_expenditures

  def pos_percent(self):
      if self.total_indy_expenditures == 0:
          return 0
      else:
          return 100*(self.ie_support_reps + self.ie_support_dems ) / self.total_indy_expenditures


  def __unicode__(self):
      return self.name        

  def has_linkable_url(self):
      """Don't display a url if someone adds a space there... """
      if (len(self.profile_url.strip()) > 4):
          return True
      return False    

  def superpac_status(self):
      if (self.is_superpac):
          return 'Y'
      else:
          return 'N'    

  def hybrid_status(self):
      if (self.is_hybrid):
          return 'Y'
      else:
          return 'N'

  def superpachackcsv(self):
      return "/outside-spenders/2014/csv/committee/%s/%s/" % (self.slug, self.fec_id) 

  def superpachackdonorscsv(self):
      return "/outside-spenders/2014/csv/contributions/%s/%s/" % (self.slug, self.fec_id)

  def filing_frequency_text(self):
      if (self.filing_frequency.upper()=='M'):
          return "Monthly"
      if (self.filing_frequency.upper()=='Q'):
          return "Quarterly"
      if (self.filing_frequency.upper()=='T'):
          return "Terminated"
      if (self.filing_frequency.upper()=='W'):
          return "Waived"
      if (self.filing_frequency.upper()=='A'):
          return "Administratively Terminated"            



  def display_type(self):
      key = self.ctype
      try:
          return type_hash[key]
      except KeyError:
          return ''


  def display_political_orientation(self):
      p = self.political_orientation
      if p=='D':
          return "Backs Democrats"
      if p=='R':
          return "Backs Republicans"
      else:
          return "Unassigned"




# because this is defined by cycle, not every state has a senator; others are represented twice, if there's a special senate election.
class District(models.Model):
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    state = models.CharField(max_length=2, blank=True, null=True, choices=STATE_CHOICES, help_text="US for president")
    incumbent_legislator = models.ForeignKey(Legislator, null=True)
    office = models.CharField(max_length=1, null=True,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President')))
    office_district = models.CharField(max_length=2, blank=True, null=True, help_text="'00' for at-large congress; null for senate, president")
    term_class = models.IntegerField(blank=True, null=True, help_text="1,2 or 3. Pulled from US Congress repo. Only applies to senators.")
    incumbent_name = models.CharField(max_length=255, blank=True, null=True, help_text="incumbent name")
    incumbent_pty = models.CharField(max_length=3, blank=True, null=True, help_text="What party is the incumbent? 3-digit FEC abbrev")
    incumbent_party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party: D for Dem, DFL etc; R for R, more TK")
    election_year = models.IntegerField(blank=True, null=True, help_text="When is the next general election going to take place--enter this even when we don't know the election date")
    next_election_date = models.DateField(blank=True, null=True)
    next_election_code = models.CharField(max_length=2, blank=True, null=True, choices=ELECTION_TYPE_CHOICES) # General, Primary, Runoff, SP=special primary, SR=special runoff, SG=special general, Caucus, Other
    special_election_scheduled = models.NullBooleanField(default=False, null=True, help_text="Is there a special election scheduled ahead of the next regularly scheduled election?")
    open_seat = models.NullBooleanField(default=False, null=True, help_text="is the incumbent stepping down")
    # nice to have: hist
    dem_frac_historical = models.FloatField(null=True, help_text="What fraction of the time since 2000 has this seat been occupied by democrats")
    rep_frac_historical = models.FloatField(null=True, help_text="What fraction of the time since 2000 has this seat been occupied by republicans")
    altered_by_2010_redistricting = models.BooleanField(default=False,help_text="Was this district substantially changed in the 2010 redistricting ? ")

    def __unicode__(self):
        if self.office == 'P':
            return 'President'
        elif self.office == 'S':
            return '%s (Senate) %s-%s' % (self.state, self.term_class, self.election_year)
        else:
            return '%s-%s (House)' % (self.state, self.office_district)

class Candidate_Overlay(models.Model):
    ## This is the human verified field -- see legislators.models.incumbent_challenger
    is_incumbent = models.BooleanField(default=False,help_text="Are they an incumbent? If not, they are a challenger")
    # foreign key to district
    district = models.ForeignKey('District')
    # drop the foreign key to Candidate_Overlay -- these tables are dropped and recreated regularly.
    #candidate = models.ForeignKey(Candidate, null=True)
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    transparency_id = models.CharField(max_length=31, blank=True, null=True, help_text="Crosswalk to influence explorer etc.")
    is_minor_candidate = models.BooleanField(default=False,help_text="Should we hide this name because they're not a serious candidate")
    not_seeking_reelection = models.BooleanField(default=False,help_text="It's confusing if we remove incumbents, so keep them here, but note that they are retiring. ")
    other_office_sought = models.CharField(max_length=127, blank=True, null=True, help_text="E.g. are they running for senate?")
    other_fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="If they've declared for another federal position, what is it? ")
    name = models.CharField(max_length=255, blank=True, null=True, help_text="incumbent name")
    pty = models.CharField(max_length=3, blank=True, null=True, help_text="What party is the incumbent?")
    party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party")
    fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="FEC candidate id")
    pcc = models.CharField(max_length=9, blank=True, null=True, help_text="FEC id for primary campaign committee")
    election_year = models.PositiveIntegerField(blank=True, null=True, help_text="year of general election")
    state = models.CharField(max_length=2, blank=True, null=True, help_text="US for president")
    office = models.CharField(max_length=1, null=True,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              )
    office_district = models.CharField(max_length=2, blank=True, null=True, help_text="'00' for at-large congress; null for senate, president")
    term_class = models.IntegerField(blank=True, null=True, help_text="1,2 or 3. Pulled from US Congress repo. Only applies to senators.")
    bio_blurb = models.TextField(null=True, blank=True, help_text="Very short; mainly intended for non-incumbents who no one's heard of.")
    cand_ici = models.CharField(max_length=1, null=True, choices=(('I','Incumbent'), ('C', 'Challenger'), ('O', 'Open Seat')))
    candidate_status = models.CharField(max_length=2, blank=True, null=True, help_text="D=declared, U=undeclared, but has a committee raising money for the race. If they have neither a committee nor a statement of candidacy, probably shouldn't be in here. Apparently one can do the committee as a 527 org with the IRS--haven't seen this yet. ")
    
    
    
    # add on id fields
    crp_id = models.CharField(max_length=9, blank=True, null=True)
    transparencydata_id = models.CharField(max_length=40, default='', null=True)    

    #

    slug = models.SlugField()
    total_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_supporting = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    # need to add electioneering here:
    electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    
    # Is this candidate a winner in the general election?
    cand_is_gen_winner = models.NullBooleanField(null=True)

    # Are they in the general election ? 
    is_general_candidate = models.NullBooleanField(null=True)
    ### data from the candidates own committees. Can be outta date for senate. From weball. 
    cand_ttl_receipts= models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_ending_cash = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_ttl_ind_contribs = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_cand_contrib = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_cand_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_debts_owed_by = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_report_date = models.DateField(null=True)

    class Meta:
        unique_together = ('fec_id', 'cycle')
        
    def __unicode__(self):
        if self.office == 'S':
            return '%s %s (Senate) %s-%s' % (self.name, self.state, self.term_class, self.election_year)
        else:
            return '%s %s (House) %s-%s' % (self.name, self.state, self.office_district, self.election_year)
            

    def display_party(self):
        try:
            if (self.party.upper()=='REP'):
                return '(R)'
            elif (self.party.upper()=='DEM'):
                return '(D)'
            else: 
                return ''
        except AttributeError:
            return ''
        # todo--add other parties, if there are any that are being used?

    def influence_explorer_url(self):
        if not self.transparencydata_id:
            return None
        return 'http://influenceexplorer.com/politician/%s/%s' % (self.slug,
                                                                  self.transparencydata_id)


# This represents either a regular or a special election -- see subelection below. 
class Election(models.Model):
    # Foreign key to some district here, maybe? 
    # foreign key to sole winner, if there is one. 
    district = models.ForeignKey('District')
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    election_year = models.IntegerField(help_text="the year the general election is taking place; populate this even when we don't know election date. ")
    seat_redistricted = models.BooleanField(default=False,help_text="Has the district changed since the last election? If so, don't compare current race to prior")
    seat_isnew = models.BooleanField(default=False,help_text="Is this an entirely new district--that is, this district didn't exist last cycle")
    open_seat = models.BooleanField(default=False,help_text="Is the incumbent not running?")
    incumbent_name = models.CharField(max_length=255, blank=True, null=True, help_text="incumbent name")
    incumbent_pty = models.CharField(max_length=3, blank=True, null=True, help_text="What party is the incumbent? 3-digit FEC abbrev")
    incumbent_party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party: D for Dem, DFL etc; R for R, more TK")
    # foreign key to more details about incumbent ? 
    election_year = models.PositiveIntegerField(blank=True, help_text="year of general election")
    state = models.CharField(max_length=2, blank=True, null=True, help_text="US for president")
    office = models.CharField(max_length=1, null=True,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              )
    office_district = models.CharField(max_length=2, blank=True, null=True, help_text="'00' for at-large congress, senate, president") 
    term_class = models.IntegerField(blank=True, null=True, help_text="1,2 or 3. Pulled from US Congress repo. Only applies to senators.")
    election_code = models.CharField(max_length=1, blank=True, null=True, choices=ELECTION_TYPE_CHOICES) # N=Normal, S=Special
    
 
    def __unicode__(self):
        return_value = ""
        if self.office == 'S':
            return_value =  '%s (Senate) %s-%s type=%s' % (self.state, self.term_class, self.election_year, self.election_code)
        else:
            return_value = '%s (House) %s-%s type=%s' % (self.state, self.office_district, self.election_year, self.election_code)
        
        return_value += " Incumbent: %s" % (self.incumbent_name)
        return return_value

"""
primary_party = models.CharField(max_length=1, blank=True, null=True, help_text="What party is this a primary for ? ")
 primary_contested = models.NullBooleanField(default=False,help_text="Is there at least one candidate running?")
 election_code = models.CharField(max_length=2, blank=True, null=True, choices=ELECTION_TYPE_CHOICES) # General, Primary, PR=Primary runoff, GR=general runoff, SP=special primary, SR=special primary runoff, SG=special general, VR=Special general runoff, Caucus, Other
 election_other_description = models.CharField(max_length=20, blank=True, null=True, help_text="FEC field; required if election code is 'O' for other")
 
 election_date = models.DateField(null=True, help_text="The 'main' day that polls are open; this is what determines the 20-day pre election report, for example.")
 election_voting_start_date = models.DateField(null=True, help_text="The day that voting starts, be it by mail or whatever. Not sure we really care about this. ")
 election_voting_end_date = models.DateField(null=True, help_text="The day that voting ends--this is probably the election date")

"""
# a specific election--that is, either a general or a primary. 
class SubElection(models.Model):
    parentElection = models.ForeignKey('Election')
    subelection_code = models.CharField(max_length=2, blank=True, null=True, choices=ELECTION_TYPE_CHOICES) # General, Primary, PR=Primary runoff, GR=general runoff, SP=special primary, SR=special primary runoff, SG=special general, VR=Special general runoff, Caucus, Other
    election_other_description = models.CharField(max_length=20, blank=True, null=True, help_text="FEC field; required if election code is 'O' for other")
    primary_party = models.CharField(max_length=1, blank=True, null=True, help_text="If this is a primary, what party is it for? Leave empty for a general election.")
    is_contested = models.NullBooleanField(default=False,help_text="Is there at least one candidate running?")
    election_date = models.DateField(null=True, help_text="The 'main' day that polls are open; this is what determines the 20-day pre election report, for example.")
    election_voting_start_date = models.DateField(null=True, help_text="The day that voting starts, be it by mail or whatever. Not sure we really care about this. ")
    election_voting_end_date = models.DateField(null=True, help_text="The day that voting ends--this is probably the election date")

class Election_Candidate(models.Model):
    # Relates to overall election
    candidate = models.ForeignKey('Candidate_Overlay')
    race = models.ForeignKey('Election')
    is_sole_winner = models.NullBooleanField(null=True, help_text="Only true if they are the sole winner") # 
    advance_to_runoff = models.NullBooleanField(null=True, help_text="Only true if a runoff is taking place") # 
    is_loser = models.NullBooleanField(null=True) 
    vote_percent = models.FloatField(blank=True, null=True)
    vote_number = models.IntegerField(blank=True, null=True)
    ## Hmm are these official results, or unofficial? What if there's a recount? 

    def __unicode__(self):
        return "CANDIDATE: %s RACE:%s" % (self.candidate, self.race)

class SubElection_Candidate(models.Model):
    # Specific to either a general or a primary.
    candidate = models.ForeignKey('Candidate_Overlay')
    race = models.ForeignKey('Election')
    is_sole_winner = models.NullBooleanField(null=True, help_text="Only true if they are the sole winner") # 
    advance_to_runoff = models.NullBooleanField(null=True, help_text="Only true if a runoff is taking place") # 
    is_loser = models.NullBooleanField(null=True) 
    vote_percent = models.FloatField(blank=True, null=True)
    vote_number = models.IntegerField(blank=True, null=True)
    ## Hmm are these official results, or unofficial? What if there's a recount? 

    def __unicode__(self):
        return "CANDIDATE: %s RACE:%s" % (self.candidate, self.race)


## summary helpers:
"""
class Committee_Time_Summary(models.Model):
    com_id = 
    filing_number = 
    tot_receipts =
    tot_contrib = 
    tot_ite_contrib = 
    tot_non_ite_contrib = 
    tot_disburse =
    tot_loans =
    cash_on_hand_end = 
    outstanding_loans =  
    coverage_from_date = models.DateField(null=True)
    coverage_through_date = models.DateField(null=True)
    data_source =  # periodic filing; webk ; 
    
class Big_IE_Spending(models.Model):  
  
"""  
    