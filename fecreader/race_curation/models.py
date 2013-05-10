from django.db import models

#from django_localflavor_us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.us_states import STATE_CHOICES

from ftpdata.models import Candidate
from legislators.models import Legislator

STATE_CHOICES_DICT = dict(STATE_CHOICES)

ELECTION_TYPE_CHOICES = (('G', 'General'), ('P', 'Primary'), ('R', 'Runoff'), ('SP', 'Special Primary'), ('SR', 'Special Runoff'), ('SG', 'Special General'), ('O', 'Other'))

type_hash={'C':'Communication Cost',
          'D':'Delegate',
          'H':'House',
          'I': 'Not a Committee',
          'N': 'Non-Party, Non-Qualified',
          'P': 'Presidential',
          'Q': 'Qualified, Non-Party',
          'S': 'Senate',
          'X': 'Non-Qualified Party',
          'Y': 'Qualified Party',
          'Z': 'National Party Organization',
          'E': 'Electioneering Communication',
          'O': 'Super PAC'
          }

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

# Create your models here.
class Candidate_Overlay(models.Model):
    #foreign key to full fec data = models.ForeignKey(some_model)
    # foreignkeytoUScongressifthereisone = models.ForeignKey(some_model)
    # foreign key to district
    district = models.ForeignKey('District')
    candidate = models.ForeignKey(Candidate, null=True)
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    transparency_id = models.CharField(max_length=31, blank=True, null=True, help_text="Crosswalk to influence explorer etc.")
    is_minor_candidate = models.BooleanField(default=False,help_text="Should we hide this name because they're not a serious candidate")
    not_seeking_reelection = models.BooleanField(default=False,help_text="It's confusing if we remove incumbents, so keep them here, but note that they are retiring. ")
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

    class Meta:
        unique_together = ('fec_id', 'cycle')
        
    def __unicode__(self):
        if self.office == 'S':
            return '%s %s (Senate) %s-%s' % (self.name, self.state, self.term_class, self.election_year)
        else:
            return '%s %s (House) %s-%s' % (self.name, self.state, self.office_district, self.election_year)

class Election(models.Model):
    # Foreign key to some district here, maybe? 
    # foreign key to sole winner, if there is one. 
    district = models.ForeignKey('District')
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    election_year = models.IntegerField(help_text="the year the general election is taking place; populate this even when we don't know election date. ")
    election_date = models.DateField(null=True, help_text="The 'main' day that polls are open; this is what determines the 20-day pre election report, for example.")
    election_voting_start_date = models.DateField(null=True, help_text="The day that voting starts, be it by mail or whatever. Not sure we really care about this. ")
    election_voting_end_date = models.DateField(null=True, help_text="The day that voting ends--this is probably the election date")
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
    primary_party = models.CharField(max_length=1, blank=True, null=True, help_text="What party is this a primary for ? ")
    primary_contested = models.NullBooleanField(default=False,help_text="Is there at least one candidate running?")
    election_code = models.CharField(max_length=2, blank=True, null=True, choices=ELECTION_TYPE_CHOICES) # General, Primary, PR=Primary runoff, GR=general runoff, SP=special primary, SR=special primary runoff, SG=special general, VR=Special general runoff, Caucus, Other
    election_other_description = models.CharField(max_length=20, blank=True, null=True, help_text="FEC field; required if election code is 'O' for other")
    
    def __unicode__(self):
        return_value = ""
        if self.office == 'S':
            return_value =  '%s (Senate) %s-%s type=%s' % (self.state, self.term_class, self.election_year, self.election_code)
        else:
            return_value = '%s (House) %s-%s type=%s' % (self.state, self.office_district, self.election_year, self.election_code)
        if self.primary_party:
            return_value += ' party=%s' % (self.primary_party)
        return_value += " Incumbent: %s" % (self.incumbent_name)
        return return_value

class Election_Candidate(models.Model):
    ##  Could be many to many with 'through' but... 
    # foreign key to race
    # foreign key to candidate overlay
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
