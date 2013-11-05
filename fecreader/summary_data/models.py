import datetime

from django.db import models
from django.utils.text import slugify

from django.contrib.localflavor.us.us_states import STATE_CHOICES

from ftpdata.models import Candidate
from legislators.models import Legislator
from api.nulls_last_queryset import NullsLastManager
from data_references import STATES_FIPS_DICT

STATE_CHOICES_DICT = dict(STATE_CHOICES)

ELECTION_TYPE_CHOICES = (('G', 'General'), ('P', 'Primary'), ('R', 'Runoff'), ('SP', 'Special Primary'), ('SR', 'Special Runoff'), ('SG', 'Special General'), ('O', 'Other'))

type_hash_full={'C': 'Communication Cost',
          'D': 'Delegate',
          'E': 'Electioneering Communication',
          'H': 'House',
          'I': 'Not a Committee',
          'N': 'Non-Party, Non-Qualified',
          'O': 'Super PAC',
          'P': 'Presidential',
          'Q': 'Qualified, Non-Party',
          'S': 'Senate',
          'U': 'Single candidate super PAC',
          'V': 'Hybrid super PAC - Nonqualified',
          'W': 'Hybrid super PAC - Qualified',
          'X': 'Non-Qualified Party',
          'Y': 'Qualified Party',
          'Z': 'National Party Organization',
          }
          
type_hash={'C': 'Communication Cost',
        'D': 'Delegate',
        'E': 'Electioneering',
        'H': 'House',
        'I': 'Expenditure Only',
        'N': 'PAC',
        'O': 'Super PAC',
        'P': 'Presidential',
        'Q': 'PAC',
        'S': 'Senate',
        'U': 'Single candidate super PAC',
        'V': 'Hybrid super PAC',
        'W': 'Hybrid super PAC',
        'X': 'Party PAC',
        'Y': 'Party PAC',
        'Z': 'National Party PAC',
        }

committee_designation_hash = {'A':'Authorized by Candidate',
                            'J': 'Joint Fund Raiser',
                            'P': 'Principal Committee of Candidate',
                            'U': 'Unauthorized',
                            'B': 'Lobbyist/Registrant PAC',
                            'D': 'Leadership PAC'
                            }
STATES_FIPS_DICT = {
    'WA':'53',
    'VA':'51',
    'DE':'10',
    'DC':'11',
    'WI':'55',
    'WV':'54',
    'HI':'15',
    'FL':'12',
    'WY':'56',
    'NH':'33',
    'NJ':'34',
    'NM':'35',
    'TX':'48',
    'LA':'22',
    'NC':'37',
    'ND':'38',
    'NE':'31',
    'TN':'47',
    'NY':'36',
    'PA':'42',
    'CA':'06',
    'NV':'32',
    'CO':'08',
    'AK':'02',
    'AL':'01',
    'AR':'05',
    'VT':'50',
    'IL':'17',
    'GA':'13',
    'IN':'18',
    'IA':'19',
    'OK':'40',
    'AZ':'04',
    'ID':'16',
    'CT':'09',
    'ME':'23',
    'MD':'24',
    'MA':'25',
    'OH':'39',
    'UT':'49',
    'MO':'29',
    'MN':'27',
    'MI':'26',
    'RI':'44',
    'KS':'20',
    'MT':'30',
    'MS':'28',
    'SC':'45',
    'KY':'21',
    'OR':'41',
    'SD':'46'}

# There are many different data sets that are updated. Keep track of them here.
# options are "scrape_electronic_filings", "scrape_new_committees",...
class Update_Time(models.Model):
  key = models.SlugField()
  update_time = models.DateTimeField()

  def save(self, *args, **kwargs):
      ''' On save, update timestamps '''
      self.update_time = datetime.datetime.today()
      super(Update_Time, self).save(*args, **kwargs)


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
    # summary data
    
    # do these need to be differentiated between primary / general elections ? 
    candidate_raised = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    candidate_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    coordinated_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    outside_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    # should we include electioneering? 
    electioneering_spending = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    
    # This is pulled from the rothenberg app periodically
    rothenberg_rating_id = models.IntegerField(null=True)
    rothenberg_rating_text = models.CharField(null=True, max_length=63)
    rothenberg_update_time = models.DateTimeField(null=True)
    
    district_notes = models.TextField(null=True, blank=True, help_text="Mostly intended to note special elections, but...")
    
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
        return "http://rothenbergpoliticalreport.com/state/" + state_slug
            
    def __unicode__(self):
        if self.office == 'P':
            return 'President'
        elif self.office == 'S':
            return '%s (Senate) %s-%s' % (self.state, self.term_class, self.election_year)
        else:
            return '%s-%s (House)' % (self.state, self.office_district)
            
    def get_absolute_url(self):
        url= ""
        if self.office == 'H':
            url="/race/%s/%s/%s/%s/" % (self.cycle, self.office, self.state, self.office_district)
        elif self.office == 'S':
            url= "/race/%s/%s/%s/%s/" % (self.cycle, self.office, self.state, self.term_class)
        elif self.office == 'P':
            url= "/race/%s/president/" % (self.cycle)
        
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
            name="%s House Race, District %s, %s" % (STATE_CHOICES_DICT[self.state], self.office_district, self.election_year)
        elif self.office == 'S':
            name= "%s Senate Race, %s" % (STATE_CHOICES_DICT[self.state], self.election_year)
        elif self.office == 'P':
            name= "Presidential Race"
        return name
            
    def get_filtered_ie_url(self):
        return "/outside-spending/#?ordering=-expenditure_date_formatted&district_checked=%s" % self.pk

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
    not_seeking_reelection = models.BooleanField(default=False,help_text="It's confusing if we remove incumbents, so keep them here, but note that they are retiring. ")
    other_office_sought = models.CharField(max_length=127, blank=True, null=True, help_text="E.g. are they running for senate?")
    other_fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="If they've declared for another federal position, what is it? This should be the *candidate id* not a committee id. ")
    name = models.CharField(max_length=255, blank=True, null=True, help_text="incumbent name")
    pty = models.CharField(max_length=3, blank=True, null=True, help_text="What party is the incumbent?")
    party = models.CharField(max_length=1, blank=True, null=True, help_text="Simplified party")
    fec_id = models.CharField(max_length=9, blank=True, null=True, help_text="FEC candidate id")
    pcc = models.CharField(max_length=9, blank=True, null=True, help_text="FEC id for primary campaign committee")
    
    # This is displayed--this needs to be maintained.
    election_year = models.PositiveIntegerField(blank=True, null=True, help_text="year of general election")
    state = models.CharField(max_length=2, blank=True, null=True, help_text="US for president")
    office = models.CharField(max_length=1, null=True,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              )
    office_district = models.CharField(max_length=2, blank=True, null=True, help_text="'00' for at-large congress; null for senate, president")
    term_class = models.IntegerField(blank=True, null=True, help_text="1,2 or 3. Pulled from US Congress repo. Only applies to senators.")
    bio_blurb = models.TextField(null=True, blank=True, help_text="Very short; mainly intended for non-incumbents who no one's heard of. If someone is running for senate who previosly served in the house, note it here.")
    cand_ici = models.CharField(max_length=1, null=True, choices=(('I','Incumbent'), ('C', 'Challenger'), ('O', 'Open Seat')))
    candidate_status = models.CharField(max_length=2, blank=True, null=True, help_text="D=declared, U=undeclared, but has a committee raising money for the race. If they have neither a committee nor a statement of candidacy, probably shouldn't be in here. Apparently one can do the committee as a 527 org with the IRS--haven't seen this yet. ")
    
    
    
    # add on id fields
    crp_id = models.CharField(max_length=9, blank=True, null=True)
    transparencydata_id = models.CharField(max_length=40, default='', null=True)

    #

    slug = models.SlugField()
    
    # independent expenditures data
    total_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    expenditures_supporting = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    expenditures_opposing = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    # need to add electioneering here:
    electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    
    # Is this candidate a winner in the general election?
    cand_is_gen_winner = models.NullBooleanField(null=True)

    # Are they in the general election ? 
    is_general_candidate = models.NullBooleanField(null=True)
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
            return '%s (%s) %s Sen.' % (self.name, self.party, self.state)
        else:
            return '%s (%s) %s-%s' % (self.name, self.party, self.state, self.office_district)
        
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
        else:
            return 'US Rep. (%s-%s)' % (self.state, self.office_district) 

    def short_office(self):
        if self.office == 'S':
            return '(%s)' % (self.state)
        else:
            return '(%s-%s)' % (self.state, self.office_district)


        
    def next_election(self):
        if self.not_seeking_reelection:
            return ''
        else:
            return 'Next election is in %s' % (self.curated_election_year) 

    def get_absolute_url(self):
        return "/candidate/%s/%s/" % (self.slug, self.fec_id)


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
            url= "/race/%s/president/" % (self.cycle)

        return url

    def get_filtered_ie_url(self):
        return "/outside-spending/#?ordering=-expenditure_date_formatted&candidate_id_checked=%s" % self.fec_id


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
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, null=True)
    fec_id = models.CharField(max_length=9, blank=True)
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
    candidate_office = models.CharField(max_length=1, blank=True, null=True)    


    has_contributions = models.NullBooleanField(null=True, default=False)
    # total receipts
    total_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)

    outstanding_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, default=0)

    # total unitemized receipts
    total_unitemized = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    cash_on_hand = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    cash_on_hand_date = models.DateField(null=True)

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
        return ("/committee/%s/%s/" % (self.slug, self.fec_id))

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
            url = "http://query.nictusa.com/cgi-bin/fecimg/?%s" % (self.fec_id)
        else:
            url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/" % (self.fec_id)

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
            url = "http://query.nictusa.com/cgi-bin/fecimg/?%s" % (self.com_id)
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
            url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/%s/" % (self.com_id, self.filing_number)
            return url
        else:
            url = "http://query.nictusa.com/cgi-bin/fecimg/?%s" % (self.com_id)
            return url

# reference table. Has these relationships for everyone. We're not building candidate overlays for other cycles.
class Authorized_Candidate_Committees(models.Model):
    candidate_id = models.CharField(max_length=9, blank=True)
    committee_id = models.CharField(max_length=9, blank=True)
    committee_name = models.CharField(max_length=255)
    is_pcc = models.NullBooleanField(null=True) 
    com_type = models.CharField(max_length=1, help_text="committee type")
    ignore = models.BooleanField(default=False, help_text="Make this true if this isn't actually authorized.")
    # maybe we're missing a year? 
    


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
    