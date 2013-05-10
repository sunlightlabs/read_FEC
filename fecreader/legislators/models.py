from django.db import models
import unicodedata
# Create your models here.


class Legislator(models.Model):
    
    bioguide = models.CharField(max_length=15, blank=True, null=True, unique=True)
    thomas = models.CharField(max_length=15, blank=True, null=True, unique=True)
    lis= models.CharField(max_length=15, blank=True, null=True)
    govtrack = models.CharField(max_length=15, blank=True, null=True)
    opensecrets= models.CharField(max_length=15, blank=True, null=True)
    votesmart= models.CharField(max_length=15, blank=True, null=True)
    icpsr= models.CharField(max_length=15, blank=True, null=True)
    cspan = models.IntegerField(blank=True, null=True)
    wikipedia= models.CharField(max_length=127, blank=True, null=True)
    house_history = models.IntegerField(blank=True, null=True)
    bioguide_previous = models.CharField(max_length=15, blank=True, null=True)
    first_name= models.CharField(max_length=63, blank=True, null=True)
    middle_name= models.CharField(max_length=63, blank=True, null=True)
    last_name= models.CharField(max_length=127, blank=True, null=True)
    suffix= models.CharField(max_length=15, blank=True, null=True)
    nickname= models.CharField(max_length=31, blank=True, null=True)
    official_full= models.CharField(max_length=255, blank=True, null=True)
    gender= models.CharField(max_length=1, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True, auto_now=False)
    religion= models.CharField(max_length=127, blank=True, null=True)
    
    def __unicode__(self):
        namestring = unicode("%s, %s" % (self.last_name, self.first_name))
        return unicodedata.normalize('NFKD',namestring).encode('ascii','ignore')



class fec(models.Model):
    legislator = models.ForeignKey(Legislator)
    fec_id = models.CharField(max_length=9, blank=True, null=True)
    
# include all names here, both alternates and originals...     
class Other_Names(models.Model):
    legislator = models.ForeignKey(Legislator)
    first_name= models.CharField(max_length=63, blank=True, null=True)
    middle_name= models.CharField(max_length=63, blank=True, null=True)
    last_name= models.CharField(max_length=127, blank=True, null=True)
    start = models.DateField(blank=True, null=True, auto_now=False)
    end = models.DateField(blank=True, null=True, auto_now=False)
 
    
class Term(models.Model):
    legislator = models.ForeignKey(Legislator)
    term_type = models.CharField(max_length=15, blank=True, null=True)
    start= models.DateField(blank=True, null=True, auto_now=False)
    end= models.DateField(blank=True, null=True, auto_now=False)
    # Some of these states aren't states, so no US state field. 
    state = models.CharField(max_length=15, blank=True, null=True)
    district = models.CharField(max_length=5, blank=True, null=True)
    term_class = models.CharField(max_length=1, blank=True, null=True)
    state_rank = models.CharField(max_length=15, blank=True, null=True)
    party = models.CharField(max_length=63, blank=True, null=True)
    url= models.CharField(max_length=511, blank=True, null=True)
    address = models.CharField(max_length=511, blank=True, null=True)
    
    def __unicode__(self):
        return "%s, %s, %s %s %s %s" % (self.legislator.last_name, self.legislator.first_name, self.party, self.term_type, self.state, self.district)
    
    def chamber(self):
        if self.term_type=='rep':
            return "House"
        elif self.term_type=='sen':
            return "Senate"
        else:
            return self.term_type
            

        