import datetime

from django.db import models
from django.utils.text import slugify

from ftpdata.models import Candidate
from legislators.models import Legislator
from api.nulls_last_queryset import NullsLastManager
from data_references import STATES_FIPS_DICT, STATE_CHOICES_DICT, STATE_CHOICES, ELECTION_TYPE_CHOICES, ELECTION_TYPE_DICT, CANDIDATE_STATUS_CHOICES, CANDIDATE_STATUS_DICT, type_hash_full, type_hash, committee_designation_hash

# There are many different data sets that are updated. Keep track of them here.
# options are "scrape_electronic_filings", "scrape_new_committees",...
class Update_Time(models.Model):
  key = models.SlugField(max_length=255)
  update_time = models.DateTimeField()

  def save(self, *args, **kwargs):
      ''' On save, update timestamps '''
      self.update_time = datetime.datetime.today()
      super(Update_Time, self).save(*args, **kwargs)


# because this is defined by cycle, not every state has a senator; others are represented twice, if there's a special senate election.
class District(models.Model):
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="The even-numbered year that ends a two-year cycle.")
    state = models.CharField(max_length=2, blank=True, null=True, choices=STATE_CHOICES, help_text="The district's state")
    incumbent_legislator = models.ForeignKey(Legislator, null=True)
    office = models.CharField(max_length=1, null=True,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President')), help_text="'H' for House, 'S' for Senate, 'P' for President")
    office_district = models.CharField(max_length=2, blank=True, null=True, help_text="'00' for at-large congress; null for senate, president")
    term_class = models.IntegerField(blank=True, null=True, help_text="1,2 or 3. Pulled from US Congress repo. Only applies to senators.")
    incumbent_name = models.CharField(max_length=255, blank=True, null=True, help_text="incumbent name")
    incumbent_pty = models.CharField(max_length=3, blank=True, null=True, help_text="What party is the incumbent? 3-digit FEC abbrev")
    incumbent_party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party: D for Dem, DFL etc; R for R")
    election_year = models.IntegerField(blank=True, null=True, help_text="When is the next general election going to take place--enter this even when we don't know the election date")
    next_election_date = models.DateField(blank=True, null=True, help_text="Date of the next eelction")
    next_election_code = models.CharField(max_length=2, blank=True, null=True, choices=ELECTION_TYPE_CHOICES) # General, Primary, Runoff, SP=special primary, SR=special runoff, SG=special general, Caucus, Other
    special_election_scheduled = models.NullBooleanField(default=False, null=True, help_text="Is there a special election scheduled ahead of the next regularly scheduled election? This should be *false* if a special election has already been held this cycle")
    open_seat = models.NullBooleanField(default=False, null=True, help_text="is the incumbent stepping down")
    # nice to have: hist
    dem_frac_historical = models.FloatField(null=True, help_text="What fraction of the time since 2000 has this seat been occupied by democrats")
    rep_frac_historical = models.FloatField(null=True, help_text="What fraction of the time since 2000 has this seat been occupied by republicans")
    altered_by_2010_redistricting = models.BooleanField(default=False,help_text="Was this district substantially changed in the 2010 redistricting ? ")
    # summary data
    
    # do these need to be differentiated between primary / general elections ? 
    candidate_raised = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Total amount raised by candidates who've run in this district during the cycle. Doesn't include incumbents who are not seeking reelection.")
    candidate_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Total amount spent by candidates who've run in this district during the cycle. Doesn't include incumbents who are not seeking reelection.")
    coordinated_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    outside_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Total amount of independent expenditures for or against candidates in this district, not including incumbents who are not seeking reelection.")
    total_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    # should we include electioneering? 
    electioneering_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    
    # This is pulled from the rothenberg app periodically
    rothenberg_rating_id = models.IntegerField(null=True)
    rothenberg_rating_text = models.CharField(null=True, max_length=63, help_text="The Rothenberg political reports rating of this district")
    rothenberg_update_time = models.DateTimeField(null=True)
    
    district_notes = models.TextField(null=True, blank=True, help_text="Mostly intended to note special elections, but...")
    
    
    general_is_decided = models.NullBooleanField(default=False, null=True, help_text="Has the general election been decided? If so all the candidates who aren't the winner can be considered the loser. This is for the November 2014 election (or later for GA, LA); not a special (except the specials held in Nov. 2014)")
    
    def get_district_fips(self):
        if self.office == 'S':
            return None
        elif self.office == 'H':
            state_fips = STATES_FIPS_DICT[self.state]
            district = self.office_district
            district = district.zfill(2)
            return state_fips + district
        else:
            return None
    
    def rothenberg_rating_short(self):
        if self.rothenberg_rating_id == 9:
            return 'Safe Republican'
        elif self.rothenberg_rating_id == 5:
            return 'Safe Democrat'
        return self.rothenberg_rating_text
        
    def display_map(self):
        if self.office=='H':
            if self.state not in ['AK']:
                return True
        return False
    
    
    def district_formatted(self):
        if self.office == 'S':
            return "%s Sen" % (self.state)
        elif self.office== 'H':
            if self.office_district:
                return "%s-%s" % (self.state, self.office_district)
            else:
                return "%s" % (self.state) 
        elif self.office == 'P':
            return "President"
            
        return ""

    def get_rothenberg_link(self):
        # They don't have links to individual districts, but instead just link to states. Provide link back to them as a courtesy. 
        state_slug = STATE_CHOICES_DICT[self.state].lower().replace(' ','-')
        return "http://rothenberggonzales.com/state/" + state_slug
            
    def __unicode__(self):
        if self.office == 'S':
            return "%s %s Sen. (%s)" % (self.cycle, self.state, self.term_class)
        elif self.office== 'H':
            if self.office_district:
                return "%s %s-%s (House)" % (self.cycle, self.state, self.office_district)
            else:
                return "%s %s" % (self.cycle, self.state) 
        elif self.office == 'P':
            return "President"
            
        return ""
            
    def get_absolute_url(self):
        url= ""
        if self.office == 'H':
            url="/race/%s/%s/%s/%s/" % (self.cycle, self.office, self.state, self.office_district)
        elif self.office == 'S':
            url= "/race/%s/%s/%s/%s/" % (self.cycle, self.office, self.state, self.term_class)
        elif self.office == 'P':
            url= "/race/president/" 
        
        return url
        
    def get_feed_url(self):
        url= ""
        if self.office == 'H':
            url="/feeds/race/%s/%s/%s/%s/" % (self.election_year, self.office, self.state, self.office_district)
        elif self.office == 'S':
            url= "/feeds/race/%s/%s/%s/%s/" % (self.election_year, self.office, self.state, self.term_class)
        elif self.office == 'P':
            url= "/feeds/race/%s/president/" % (self.election_year)

        return url
        
    def race_name(self):
        name = ""
        if self.office == 'H':
            name="%s House, District %s" % (STATE_CHOICES_DICT[self.state], self.office_district)
        elif self.office == 'S':
            name= "%s Senate" % (STATE_CHOICES_DICT[self.state])
        elif self.office == 'P':
            name= "Presidential"
        return name
            
    def get_filtered_ie_url(self):
        return "/outside-spending/#?ordering=-expenditure_date_formatted&district_checked=%s" % self.pk
        
    def next_election(self):
        if self.next_election_code:
            return ELECTION_TYPE_DICT[self.next_election_code]
        else:
            return ""
    

    class Meta:
        ordering = ['state', '-office', 'office_district']

class Candidate_Overlay(models.Model):
    ## This is the human verified field -- see legislators.models.incumbent_challenger
    is_incumbent = models.BooleanField(default=False,help_text="Are they an incumbent? If not, they are a challenger")
    curated_election_year =  models.IntegerField(null=True, help_text="What year is their next election. Set this field--don't overwrite the fec's election year. ")
    display = models.BooleanField(default=False,help_text="Should they be displayed. Use this = False for off cycle candidates.")
    
    # foreign key to district
    district = models.ForeignKey('District', null=True, help_text="Presidents have no district")
    # drop the foreign key to Candidate_Overlay -- these tables are dropped and recreated regularly.
    #candidate = models.ForeignKey(Candidate, null=True)
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    transparency_id = models.CharField(max_length=31, blank=True, null=True, help_text="Crosswalk to influence explorer etc.")
    is_minor_candidate = models.BooleanField(default=False,help_text="Should we hide this name because they're not a serious candidate")
    not_seeking_reelection = models.BooleanField(default=False,help_text="True if they are an incumbent who is not seeking reelection.")
    other_office_sought = models.CharField(max_length=127, blank=True, null=True, help_text="E.g. are they running for senate?")
    other_fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="If they've declared for another federal position, what is it? This should be the *candidate id* not a committee id. ")
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Incumbent name")
    pty = models.CharField(max_length=3, blank=True, null=True, help_text="What party is the incumbent?")
    party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party")
    fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="FEC candidate id")
    pcc = models.CharField(max_length=9, blank=True, null=True, help_text="FEC id for the candidate's primary campaign committee")
    
    # This is displayed--this needs to be maintained.
    election_year = models.PositiveIntegerField(blank=True, null=True, help_text="Year of general election")
    state = models.CharField(max_length=2, blank=True, null=True, help_text="US for president")
    office = models.CharField(max_length=1, null=True,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              )
    office_district = models.CharField(max_length=2, blank=True, null=True, help_text="'00' for at-large congress; null for senate, president")
    term_class = models.IntegerField(blank=True, null=True, help_text="1,2 or 3. Pulled from US Congress repo. Only applies to senators.")
    bio_blurb = models.TextField(null=True, blank=True, help_text="Very short; mainly intended for non-incumbents who no one's heard of. If someone is running for senate who previosly served in the house, note it here.")
    cand_ici = models.CharField(max_length=1, null=True, choices=(('I','Incumbent'), ('C', 'Challenger'), ('O', 'Open Seat')))
    candidate_status = models.CharField(max_length=2, blank=True, null=True, choices=CANDIDATE_STATUS_CHOICES, help_text="leave this blank until an election has been held--this is really a 'how did they lose' type of field.")
    
    
    
    # add on id fields
    crp_id = models.CharField(max_length=9, blank=True, null=True)
    transparencydata_id = models.CharField(max_length=40, default='', null=True)

    #

    slug = models.SlugField(max_length=255)
    
    # independent expenditures data
    total_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    expenditures_supporting = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    expenditures_opposing = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    # need to add electioneering here:
    electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    
    # Is this candidate a winner in the general election?
    cand_is_gen_winner = models.NullBooleanField(null=True, verbose_name="Candidate is general winner", help_text="Did this candidate win the general election. Only applies to November 2014 contests--so no special elections. If it's Louisiana or GA that goes to post-november runoff, do not check this box until they've won the runoff.")

    # Are they in the general election ? 
    is_general_candidate = models.NullBooleanField(null=True, verbose_name="Is a general candidate", help_text="Is this candidate in the general election and a major party candidate? Set this to true if they are a significant third party candidate too. This only controls whether or note they show up on the results pages (as a general election loser)")
    ### data from the candidates own committees. 
    
    has_contributions = models.NullBooleanField(null=True, default=False)
    # total receipts
    total_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)

    outstanding_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, default=0)

    # total unitemized receipts
    total_unitemized = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)

    cash_on_hand = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    cash_on_hand_date = models.DateField(null=True)
    
    ## these two are currently not populated
    cand_cand_contrib = models.DecimalField(max_digits=19, decimal_places=2, null=True, help_text="contributions from the candidate herself")
    cand_cand_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, help_text="loans from the candidate herself")
        

    class Meta:
        unique_together = ('fec_id', 'cycle')
    
    def __unicode__(self):
        if self.office == 'S':
            return '%s (%s) %s Sen. [%s]' % (self.name, self.party, self.state, self.cycle)
        elif self.office == 'P':
            return '%s (%s) President [%s]' % (self.name, self.party, self.cycle)           
        else:
            return '%s (%s) %s-%s [%s]' % (self.name, self.party, self.state, self.office_district, self.cycle)
        
    def incumbency_status(self):
        if self.is_incumbent:
            return "Y"
        else:
            return "N"
    
    def is_electronic_filer(self):
        if self.office == 'S':
            return False
        else:
            return True
    
    def detailed_office(self):
        if self.office == 'S':
            return 'US Sen. (%s)' % (self.state)
        elif self.office == 'H':
            return 'US Rep. (%s-%s)' % (self.state, self.office_district) 
        elif self.office == 'P':
            return 'US President'
        else:
            return ''

    def short_office(self):
        if self.office == 'S':
            return '(%s)' % (self.state)
        elif self.office == 'H':
            return '(%s-%s)' % (self.state, self.office_district)
        elif self.office == 'P':
            return 'President'
        else:
            return ""
        

    def has_next_election(self):
        try:
            if self.not_seeking_reelection or len(self.candidate_status) > 0:
                return False
        except TypeError:
            pass
        return True
        

    def get_absolute_url(self):
        return "/candidate/%s/%s/%s/" % (self.cycle, self.slug, self.fec_id)


    def display_party(self):
        if (self.party):
            return "(%s)" % (self.party.upper())
        else: 
            return ''


    def influence_explorer_url(self):
        if not self.transparencydata_id:
            return None
        return 'http://influenceexplorer.com/politician/%s/%s' % (self.slug,
                                                                  self.transparencydata_id)



    def get_race_url(self):
        url= ""
        if self.office == 'H':
            url="/race/%s/%s/%s/%s/" % (self.cycle, self.office, self.state, self.office_district)
        elif self.office == 'S':
            url= "/race/%s/%s/%s/%s/" % (self.cycle, self.office, self.state, self.term_class)
        elif self.office == 'P':
            # may want to change this later
            url= "/presidential/"

        return url

    def get_filtered_ie_url(self):
        return "/outside-spending/#?ordering=-expenditure_date_formatted&candidate_id_checked=%s" % self.fec_id
    
    def show_candidate_status(self):
        if self.cand_is_gen_winner and self.is_general_candidate:
            return "Won General"
        
        if self.cand_is_gen_winner == False and self.is_general_candidate:
            return "Lost General"
        
        if self.candidate_status:
            try: 
                return CANDIDATE_STATUS_DICT[self.candidate_status]
            except KeyError:
                return ""
        return ""

    def get_general_status(self):
        if self.cand_is_gen_winner==None and self.is_general_candidate:
            return "Not decided"
        elif self.cand_is_gen_winner and self.is_general_candidate:
            return "Won General"
        elif not self.cand_is_gen_winner and self.is_general_candidate:
            return "Lost General"
        elif not self.is_general_candidate:
            return "Not a general candidate"
        else:
            return ""

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
    curated_candidate = models.ForeignKey('Candidate_Overlay', related_name='related_candidate', null=True, help_text="For house and senate: Only include if it's a P-primary campaign committee or A-authorized campaign committee with the current cycle as appears in the candidate-committee-linkage file. Check this by hand for presidential candidates though, because many committees claim to be authorized by aren't")
    
    is_dirty = models.NullBooleanField(null=True, default=True, help_text="Do summary numbers need to be recomputed?")    
    

    # direct from the raw fec table
    name = models.CharField(max_length=255, help_text="The committee name.")
    display_name = models.CharField(max_length=255, null=True)
    fec_id = models.CharField(max_length=9, blank=True, help_text="The FEC id of the filing committee")
    slug = models.SlugField(max_length=255)
    party = models.CharField(max_length=3, blank=True, null=True)
    treasurer = models.CharField(max_length=200, blank=True, null=True)
    street_1 = models.CharField(max_length=34, blank=True, null=True)
    street_2 = models.CharField(max_length=34, blank=True, null=True)
    city =models.CharField(max_length=30, blank=True, null=True)
    zip_code = models.CharField(max_length=9, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True, help_text='the state where the pac mailing address is')
    connected_org_name=models.CharField(max_length=200, blank=True, null=True)
    filing_frequency = models.CharField(max_length=1, blank=True, null=True)

    candidate_id = models.CharField(max_length=9,blank=True, null=True)
    candidate_office = models.CharField(max_length=1, blank=True, null=True, help_text="The office of the candidate that this committee supports. Not all committees support candidates.")    


    has_contributions = models.NullBooleanField(null=True, default=False)
    # total receipts
    total_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Total receipts for this committee ceived during the entire cycle. ")
    total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Total disbursements by this committee ceived during the entire cycle")

    outstanding_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, default=0, help_text="Total outstanding loans as of the cash_on_hand_date")

    # total unitemized receipts
    total_unitemized = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    cash_on_hand = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="Cash on hand as of the end of committee's most recent periodic report; this date appears as cash_on_hand_date")
    cash_on_hand_date = models.DateField(null=True, help_text="The end of the most recent periodic filing; the date that the cash on hand was reported as of.")

    # independent expenditures
    has_independent_expenditures = models.NullBooleanField(null=True, default=False)
    total_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True, help_text="Total independent expenditures made this cycle.")
    ie_support_dems = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to support Democratic candidates")
    ie_oppose_dems = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to oppose Democratic candidates")
    ie_support_reps = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to support Republican candidates")
    ie_oppose_reps = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0, help_text="The total amount of independent expenditures make to oppose Republican candidates")
    total_presidential_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    # Typically only party committees make coordinated expenditures
    has_coordinated_expenditures = models.NullBooleanField(null=True, default=False)
    total_coordinated_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    has_electioneering = models.NullBooleanField(null=True, default=False)
    total_electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)

      ## new

    # what kinda pac is it? 
    is_superpac = models.NullBooleanField(null=True, default=False)    
    is_hybrid = models.NullBooleanField(null=True, default=False)  
    is_noncommittee = models.NullBooleanField(null=True, default=False)


    org_status = models.CharField(max_length=31,
        choices=(('501(c)(4)', '501(c)(4)'),
                 ('501(c)(5)', '501(c)(5)'),
                 ('501(c)(6)', '501(c)(6)'),
                 ('527', '527'),
                 ('LLC', 'LLC'), 
                 ('Other private business', 'Other private business'),
                 ('Public business', 'Public business'),
                 ('Individual', 'individual'),
        ),
        blank=True, null=True, help_text="We're only tracking these for non-committees")

    # what's their orientation
    political_orientation = models.CharField(max_length=1,null=True, help_text="The political orientation of the group, as coded by sunlight algorithms / researchers. This is only added for groups making independent expenditures.", choices=[
                        ('R', 'backs Republicans'),
                        ('D', 'backs Democrats'),
                        ('U', 'unknown'),
                        ('B', 'business group supporting candidates on both sides.'),
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
                        help_text="The FEC defined committee type.",
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

    
    # roi stuff
    support_unclassified = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    oppose_unclassified = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    support_winners = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    oppose_winners = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    support_losers = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    oppose_losers = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    
    roi = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    
    # make nulls sort last
    objects = models.Manager()
    nulls_last_objects = NullsLastManager()

    class Meta:
        unique_together = (("cycle", "fec_id"),)
        ordering = ('-total_indy_expenditures', )
        
    def candidate_url(self):
        if self.curated_candidate:
            return self.curated_candidate.get_absolute_url()
        else:
            return None
            
    def curated_candidate_name(self):
        if self.curated_candidate:
            return '%s (%s)' % (self.curated_candidate.name, self.curated_candidate.party)
        else:
            return None
    
    def display_coh_date(self):
        if self.ctype=='I':
            return ""
        else:
            return self.cash_on_hand_date
    
    def display_coh(self):
        if self.ctype=='I':
            return ""
        else:
            return self.cash_on_hand

    
    def is_electronic_filer(self):
        return self.is_paper_filer == False
    
    def curated_candidate_office(self):
        if self.curated_candidate:
            if self.curated_candidate.office == 'S':
                return '%s (Senate)' % (self.curated_candidate.state)
            else:
                return '%s-%s' % (self.curated_candidate.state, self.curated_candidate.office_district)
        else:
            return None

    def get_absolute_url(self):  
        return ("/committee/%s/%s/%s/" % (self.cycle, self.slug, self.fec_id))
        
    def get_cycle_url(self, cycle):
        return ("/committee/%s/%s/%s/" % (cycle, self.slug, self.fec_id))
        

    def is_not_a_committee(self):
        if self.ctype=='I':
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
        
    def fec_all_filings(self):
        url = ""
        if self.is_paper_filer:
            url = "http://docquery.fec.gov/cgi-bin/fecimg/?%s" % (self.fec_id)
        else:
            url = "http://docquery.fec.gov/cgi-bin/dcdev/forms/%s/" % (self.fec_id)

        return url

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

    def filing_frequency_text(self):
        if (self.filing_frequency):
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
        else:
            return "Unknown"


    def display_type(self):
        key = self.ctype
        returnval = ''
        try:
            returnval = type_hash[key]
        except KeyError:
            pass
        if self.designation == 'D':
            returnval += " (Leadership PAC)"
        elif self.designation == 'J':
            returnval += " (Joint Fundraising PAC)"
        return returnval

    def display_designation(self):
        key = self.designation
        try:
            return committee_designation_hash[key]
        except KeyError:
            return ''

    def major_activity(self):
        if (self.ie_oppose_dems or self.ie_oppose_reps or self.ie_support_dems or self.ie_support_reps):
            activity_dict = {'attacking Democrats':self.ie_oppose_dems, 'attacking Republicans':self.ie_oppose_reps, 'supporting Democrats':self.ie_support_dems, 'supporting Republicans':self.ie_support_reps}
            activity_rank = sorted(activity_dict.items(), key=lambda (k, v): (v), reverse=True)
            return activity_rank[0][0]
        else:
            return ""
    
    def get_formatted_roi(self):
        return str(self.roi*100) + "%"
    
    def total_unclassified(self):
        return 0.00 + float(self.support_unclassified or 0) +  float(self.oppose_unclassified or 0)
    
    def get_ge_spending(self):
        return 0.00 + float(self.support_winners or 0) +  float(self.oppose_winners or 0) + float(self.support_losers or 0) +  float(self.oppose_losers or 0) + float(self.support_unclassified or 0) +  float(self.oppose_unclassified or 0)

    def get_pos_ge_spending(self):
        return 0.00 + float(self.support_winners or 0)  + float(self.support_losers or 0) + float(self.support_unclassified or 0)

    def get_neg_ge_spending(self):
        return 0.00 + float(self.oppose_winners or 0) +  float(self.oppose_losers or 0) +  float(self.oppose_unclassified or 0)
        
    def display_political_orientation(self):
        p = self.political_orientation
        
        if p=='D':
            return "Backs Democrats"
        elif p=='R':
            return "Backs Republicans"
        else:
            return "Unassigned"
            
    def get_filtered_ie_url(self):
        return "/outside-spending/#?ordering=-expenditure_date_formatted&filer_committee_id_number=%s" % (self.fec_id)


# This is the summary of an entire election--it's either special or normal. A normal election will be related to a primary and a general--and any associated runoffs. The scheduled runoff dates in this model are just the dates that *could* happen; the primary_runoff_needed and general_runoff_needed flags actually say whether one happened. 
class ElectionSummary(models.Model):
    district = models.ForeignKey('District', editable=False)
    incumbent_name = models.CharField(max_length=255, blank=True, null=True, help_text="incumbent name")
    incumbent_party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party: D for Dem, DFL etc; R for R, more")
    
    election_winner = models.ForeignKey('Candidate_Overlay', null=True, blank=True, help_text="This is only for the winner of the whole election--do not enter a primary winner here!")
    # alter table summary_data_electionsummary alter column election_winner_id drop not null;
    
    # election_party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party: D for Dem, DFL etc; R for R, more")
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    election_year = models.IntegerField(help_text="the year the general election is taking place; populate this even when we don't know election date. ")
    election_date = models.DateField(null=True, help_text="The 'main' day that polls are open; this is what determines the 20-day pre election report, for example.")
    election_summary_code = models.CharField(max_length=2, blank=True, null=True, choices=ELECTION_TYPE_CHOICES) # N=Normal, S=Special
    
    
    has_primary_runoff = models.NullBooleanField(default=False,help_text="Is there a primary runoff election possible?")
    primary_runoff_date = models.DateField(null=True, help_text="Leave this blank if a primary runoff isn't possible.")
    primary_runoff_needed = models.NullBooleanField(default=False,help_text="Is there a primary runoff taking place?")
    
    # General runoffs are only a Louisiana thing; also maybe georgia? 
    has_general_runoff = models.NullBooleanField(default=False,help_text="Is there a general runoff election possible?")
    general_runoff_date =  models.DateField(null=True, help_text="Leave this blank if there is no general runoff election possible.")
    general_runoff_needed = models.NullBooleanField(default=False,help_text="Is there a general runoff taking place?")
    
    
    candidate_raised = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    candidate_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    coordinated_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    outside_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)

    def __unicode__(self):
        return "%s (%s) - %s (%s)" % (self.district, self.election_summary_code, self.district.incumbent_name, self.district.incumbent_party)

# This is a single day that people vote--could be a primary, a primary runoff, a general, a general runoff, a special primary, a special primary runoff, a special general, or a special general runoff. 
class Election(models.Model):
    
    district = models.ForeignKey('District')
    election = models.ForeignKey('ElectionSummary')
    
    # This is only populated if there is a single winner ? I guess this should be a many-to-many field ? 
    election_winner = models.ForeignKey('Candidate_Overlay', null=True)
    # alter table summary_data_election alter column election_winner_id drop not null;
    
    # We just have a primary election -- its too hard to say whether outside money is involved in a particular side of a primary
    # election_party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party: D for Dem, DFL etc; R for R, more")
    
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    election_year = models.IntegerField(help_text="the year the general election is taking place; populate this even when we don't know election date. ")
    # what day did the primary start? If this is a general election, when did the primaries for this election start? 
    start_date = models.DateField(null=True)
    
    election_date = models.DateField(null=True, help_text="The 'main' day that polls are open; this is what determines the 20-day pre election report, for example.")    
    
    election_code = models.CharField(max_length=2, blank=True, null=True, choices=ELECTION_TYPE_CHOICES) 
    
    election_other_description = models.CharField(max_length=20, blank=True, null=True, help_text="FEC field; required if election code is 'O' for other")
    
    is_contested = models.NullBooleanField(default=False,help_text="Is there at least one candidate running?")
    
    candidate_raised = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    candidate_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    coordinated_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    outside_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    
 
    def __unicode__(self):
        return_value = ""
        if self.office == 'S':
            return_value =  '%s (Senate) %s-%s type=%s' % (self.state, self.term_class, self.election_year, self.election_code)
        else:
            return_value = '%s (House) %s-%s type=%s' % (self.state, self.office_district, self.election_year, self.election_code)
        
        return_value += " Incumbent: %s" % (self.incumbent_name)
        return return_value


## summary helpers:

class Committee_Time_Summary(models.Model):
    com_id = models.CharField(max_length=9, blank=True)
    com_name = models.CharField(max_length=255, null=True, blank=True)
    filing_number = models.IntegerField(null=True, blank=True, help_text="Not applicable for webk")
    tot_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    tot_contrib = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    tot_ite_contrib = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    tot_non_ite_contrib = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    tot_disburse =models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)

    ind_exp_mad = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, help_text="independent expenditures made")
    coo_exp_par = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, help_text="coordinated expenditures made (party committees only)")
    new_loans =models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    outstanding_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, help_text="in webk this is deb_owe_by_com")
    electioneering_made = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, help_text="not in webk")
    cash_on_hand_end = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    coverage_from_date = models.DateField(null=True)
    coverage_through_date = models.DateField(null=True)
    data_source = models.CharField(max_length=10, help_text="webk|electronic")

    # also appears in the newfiling model--normalize this. 
    def get_absolute_url(self):
        if self.filing_number:
            return "/filings/%s/" % (self.filing_number)
        else:
            url = "http://docquery.fec.gov/cgi-bin/fecimg/?%s" % (self.com_id)
            return url
    
    def get_committee_url(self):
        return "/committee/%s/%s/" % (  slugify(self.com_name), self.com_id)
        
    def get_skeda_url(self):
        if self.filing_number:
            return "/filings/%s/SA/" % (self.filing_number)
        else:
            return None

    def get_skedb_url(self):
        if self.filing_number:
            return "/filings/%s/SB/" % (self.filing_number)
        else:
            return None
            
    def get_fec_url(self):
        
        if self.filing_number:
            url = "http://docquery.fec.gov/cgi-bin/dcdev/forms/%s/%s/" % (self.com_id, self.filing_number)
            return url
        else:
            url = "http://docquery.fec.gov/cgi-bin/fecimg/?%s" % (self.com_id)
            return url

    def __unicode__(self):
        return "%s: (%s-%s)" % (self.com_name, self.coverage_from_date, self.coverage_through_date)

# reference table. Has these relationships for everyone. We're not building candidate overlays for other cycles.
## 
class Authorized_Candidate_Committees(models.Model):
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    candidate_id = models.CharField(max_length=9, blank=True)
    committee_id = models.CharField(max_length=9, blank=True)
    committee_name = models.CharField(max_length=255)
    is_pcc = models.NullBooleanField(null=True) 
    com_type = models.CharField(max_length=1, help_text="committee type")
    ignore = models.BooleanField(default=False, help_text="Make this true if this isn't actually authorized.")
    # maybe we're missing a year? 
    

""" Not used, see below.

## This is untenable, I think; mismatched filing periods make this a total pain. 
class Candidate_Time_Summary(models.Model):
    candidate_id = models.CharField(max_length=9, blank=True)
    filing_number = models.IntegerField(null=True, blank=True, help_text="Not applicable for webk")
    tot_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    tot_contrib = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    tot_ite_contrib = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    tot_non_ite_contrib = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    tot_disburse =models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    new_loans =models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    outstanding_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, help_text="in webk this is deb_owe_by_com")
#    electioneering_made = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, help_text="not in webk")
    cash_on_hand_end = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    coverage_from_date = models.DateField(null=True)
    coverage_through_date = models.DateField(null=True)
    data_source = models.CharField(max_length=10, help_text="webk|electronic")

"""


# This is only used during testing. 
class Filing_Gap(models.Model):
    # record-keeping for what filings are missing. 
    # Will attempt to backfill with webk data to handle case of 
    # pac that's switched from paper to electronic, or otherwise
    # done something weird. 
    
    committee_id = models.CharField(max_length=9, blank=True)
    gap_start = models.DateField(null=True)
    gap_end = models.DateField(null=True)




""" outside spending tables. Doesn't include communication cost.  """


# pac_candidate -- indicates a pac's total support or opposition towards a particular candidate. If a particular pac *both* supports and opposes a candidate, this should go in two separate entries. 
class Pac_Candidate(models.Model):
    cycle = models.CharField(max_length=4, null=True, blank=True)
    committee = models.ForeignKey('Committee_Overlay')
    candidate = models.ForeignKey('Candidate_Overlay')
    support_oppose = models.CharField(max_length=1, 
                                       choices=(('S', 'Support'), ('O', 'Oppose'))
                                       )
    total_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True) 
    total_ec = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_coord_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True) 

    class Meta:
        ordering = ('-total_ind_exp', )

    def __unicode__(self):
        return self.committee, self.candidate

    def support_or_oppose(self):
        if (self.support_oppose.upper() == 'O'):
            return '<div class="label-oppose">Oppose</div>'
        elif (self.support_oppose.upper() == 'S'): 
            return '<div class="label-support">Support</div>'
        return ''

class State_Aggregate(models.Model):    
    cycle = models.CharField(max_length=4, null=True, blank=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    expenditures_supporting_president = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing_president = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_pres_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_supporting_house = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing_house = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_house_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)   
    expenditures_supporting_senate = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing_senate = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_senate_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)     
    total_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    # last 10 days is recent
    recent_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    recent_pres_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_ec = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_coord = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    def __unicode__(self):
        return STATE_CHOICES[self.state]

    def get_absolute_url(self):
        return "/state/%s/" % (self.state)

class DistrictWeekly(models.Model):
    # weekly summary of race activity. Maybe truncate at $1000 or more? 
    district = models.ForeignKey('District')
    # what day did the primary start? If this is a general election, when did the primaries for this election start? 
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True, help_text="The 'main' day that polls are open; this is what determines the 20-day pre election report, for example.")
    
    # This is the week number in terms of the isocalendar week number--weeks end on sunday. 
    # (year, week, day) = datetime.date(2014,3,5).isocalendar()
    # cycle_week_number = (52*(year-2013)) + week    
    cycle_week_number = models.IntegerField(null=True, blank=True, help_text="Not applicable for webk")    
    coordinated_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    outside_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)

    # make nulls sort last
    objects = models.Manager()
    nulls_last_objects = NullsLastManager()

# this is like PAC_Candidate, but is only for general election ies to be used for the ROI stuff
class roi_pair(models.Model):
    committee = models.ForeignKey('Committee_Overlay')
    candidate = models.ForeignKey('Candidate_Overlay')
    support_oppose = models.CharField(max_length=1, 
                                       choices=(('S', 'Support'), ('O', 'Oppose'))
                                       )    
    total_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True) 
    
    def show_support_oppose(self):
        if self.support_oppose.upper()=='S':
            return 'Support'
        elif self.support_oppose.upper()=='O':
            return 'Oppose'
        else:
            return 'Unknown'
    
    def verdict(self):
        """ hack for ROI """
        
        if self.candidate.cand_is_gen_winner == None:
            return ""
            
        if self.candidate.cand_is_gen_winner == True:
            if self.support_oppose.upper() == 'S':
                return '<span class="success">success</span>'
            elif self.support_oppose.upper() == 'O':
                return '<span class="failure">failure</span>'
            else:
                return ""
                
        if self.candidate.cand_is_gen_winner == False:
            if self.support_oppose.upper() == 'S':
                return '<span class="failure">failure</span>'
            elif self.support_oppose.upper() == 'O':
                return '<span class="success">success</span>'
            else:
                return ""
                
        return ""
            
    
