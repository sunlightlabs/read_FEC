from django.db import models



# these are the fec's models; only change is a cycle is added, and file source for the contribs


# populated from fec's candidate master
# http://www.fec.gov/finance/disclosure/metadata/DataDictionaryCandidateMaster.shtml

class Candidate(models.Model):
    cycle = models.PositiveIntegerField()
    cand_id = models.CharField(max_length=9, blank=True)
    cand_name = models.CharField(max_length=200,blank=True, null=True) 
    cand_pty_affiliation = models.CharField(max_length=3, blank=True, null=True)
    cand_election_year = models.PositiveIntegerField(blank=True)
    cand_office_st = models.CharField(max_length=2, blank=True, null=True, help_text="US for president")
    cand_office = models.CharField(max_length=1, null=True,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              )
    cand_office_district = models.CharField(max_length=2, blank=True, null=True, help_text="'00' for at-large congress, senate, president")                          
    cand_ici = models.CharField(max_length=1, null=True,
                                  choices=(('C', 'CHALLENGER'), ('I', 'INCUMBENT'), ('O', 'OPEN SEAT'))
                                   )
    cand_status = models.CharField(max_length=1, null=True,
                                        choices=(('C', 'STATUTORY CANDIDATE'), ('F', 'STATUTORY CANDIDATE FOR FUTURE ELECTION'), ('N', 'NOT YET A STATUTORY CANDIDATE'), ('P', 'STATUTORY CANDIDATE IN PRIOR CYCLE'))
                                         )
    cand_pcc = models.CharField(max_length=9, blank=True, null=True)
    cand_st1 = models.CharField(max_length=34, blank=True, null=True)
    cand_st2 = models.CharField(max_length=34, blank=True, null=True)
    cand_city = models.CharField(max_length=30, blank=True, null=True)
    cand_st = models.CharField(max_length=2, blank=True, null=True)
    cand_zip = models.CharField(max_length=9, blank=True, null=True)


    def __unicode__(self):
        if self.cand_office == 'S':
            return '%s (Senate) %s %s %s' % (self.cand_name, self.cand_office_st, self.cand_pty_affiliation,  self.cand_election_year)
        elif self.cand_office == 'H':
            return '%s %s (House) %s %s %s' % (self.cand_name, self.cand_office_st, self.cand_pty_affiliation,  self.cand_office_district, self.cand_election_year)
        else:
            return self.cand_name
        
# http://www.fec.gov/finance/disclosure/metadata/DataDictionaryCommitteeMaster.shtml
# Populated from fec's committee master            
class Committee(models.Model):
    cycle = models.PositiveIntegerField()
    cmte_id = models.CharField(max_length=9)
    cmte_name = models.CharField(max_length=200, null=True)
    tres_nm = models.CharField(max_length=90, blank=True, null=True)
    cmte_st1 = models.CharField(max_length=34, blank=True, null=True)
    cmte_st2 = models.CharField(max_length=34, blank=True, null=True)
    cmte_city = models.CharField(max_length=30, blank=True, null=True)
    cmte_st = models.CharField(max_length=2, blank=True, null=True)
    cmte_zip = models.CharField(max_length=9, blank=True, null=True)
    cmte_dsgn = models.CharField(max_length=1,
                           blank=False,
                           null=True,
                           choices=[('A', 'Authorized by Candidate'),
                                    ('J', 'Joint Fund Raiser'),
                                    ('P', 'Principal Committee of Candidate'),
                                    ('U', 'Unauthorized'),
                                    ('B', 'Lobbyist/Registrant PAC'),
                                    ('D', 'Leadership PAC')])



    cmte_tp = models.CharField(max_length=1,
                              blank=False,
                              null=True,
                              # V, W are Carey committees
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
    cmte_pty_affiliation = models.CharField(max_length=3, blank=True, null=True)
    cmte_filing_freq = models.CharField(max_length=1,  null=True,
        choices=[('A', 'ADMINISTRATIVELY TERMINATED'),
                 ('D', 'DEBT'),
                 ('M', 'MONTHLY FILER'),
                 ('Q', 'QUARTERLY FILER'),
                 ('T', 'TERMINATED'),
                 ('W', 'WAIVED')
                 ])

    org_tp= models.CharField(max_length=1, null=True, choices=[
                    ('C', 'CORPORATION'),
                    ('L', 'LABOR ORGANIZATION'),
                    ('M', 'MEMBERSHIP ORGANIZATION'),
                    ('T', 'TRADE ASSOCIATION'),
                    ('V', 'COOPERATIVE'),
                    ('W', 'CORPORATION WITHOUT CAPITAL STOCK')
                  ])
    connected_org_nm=models.CharField(max_length=200, blank=True,  null=True)
    cand_id = models.CharField(max_length=9, blank=True, null=True)


# Description
# http://www.fec.gov/finance/disclosure/metadata/DataDictionaryCandCmteLinkage.shtml
# file is: ftp://ftp.fec.gov/FEC/2012/ccl12.zip

# Candidate committee linkage

class CandComLink(models.Model):
    cycle = models.PositiveIntegerField()
    cand_id = models.CharField(max_length=9, null=True)
    cand_election_yr = models.PositiveIntegerField(null=True)
    fec_election_yr= models.PositiveIntegerField(null=True)
    cmte_id = models.CharField(max_length=9, null=True)
    cmte_tp = models.CharField(max_length=1,
                             blank=False,
                             null=True,
                             # V, W are Carey committees
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
    cmte_dsgn = models.CharField(max_length=1,
                                 blank=False,
                                 null=True,
                                 choices=[
                                        ('A', 'Authorized by Candidate'),
                                        ('B', 'Lobbyist/Registrant PAC'),
                                        ('D', 'Leadership PAC'),
                                        ('J', 'Joint Fund Raiser'),
                                        ('P', 'Principal Committee of Candidate'),
                                        ('U', 'Unauthorized')
                                        ])

    linkage_id= models.PositiveIntegerField()
    
# oth: http://www.fec.gov/finance/disclosure/metadata/DataDictionaryCommitteetoCommittee.shtml
# pas2: http://www.fec.gov/finance/disclosure/metadata/DataDictionaryContributionstoCandidates.shtml
# indiv: http://www.fec.gov/finance/disclosure/metadata/DataDictionaryContributionsbyIndividuals.shtml


# This contains entries from the OTH, PAS2 and INDIV datasets with two additions: filesource is the name of the file they are from and cycle is the 4-digit cycle represented. 
class contribs(models.Model):
    filesource = models.CharField(max_length=5)
    cycle = models.PositiveIntegerField()
    cmte_id = models.CharField(max_length=9, null=True)
    amndt_ind = models.CharField(max_length=1,
                                 blank=False,
                                 null=True,
                                 choices=[
                                        ('A', 'Amended'),
                                        ('N', 'New'),
                                        ('T', 'Termination'),                                        
                                        ])
    rpt_tp = models.CharField(max_length=3, null=True)
    transaction_pgi = models.CharField(max_length=9, null=True, help_text="EYYYY - E for election type, YYYY for election year")
    image_num = models.CharField(max_length=11, null=True)
    transaction_tp = models.CharField(max_length=9, null=True, help_text="transaction type")
    entity_tp = models.CharField(max_length=3,
                                 blank=False,
                                 null=True,
                                 choices=[
                                        ('CAN', 'Candidate'),
                                        ('CCM', 'Candidate Committee'),
                                        ('COM', 'Committee'),     
                                        ('IND', 'Individual'),
                                        ('ORG', 'Organization-not party or person'),
                                        ('PAC', 'PAC'),
                                        ('PTY', 'Party organization'),                                                                                                                   
                                        ])
    name = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=30, null=True)
    state = models.CharField(max_length=2, null=True)
    zip_code = models.CharField(max_length=9, null=True)
    employer = models.CharField(max_length=38, null=True)
    occupation = models.CharField(max_length=38, null=True)
    transaction_dt = models.CharField(max_length=8, null=True)
    transaction_amt = models.DecimalField(max_digits=14, decimal_places=2)
    other_id = models.CharField(max_length=9, null=True)
    # is null for some:
    cand_id = models.CharField(max_length=9, null=True)
    tran_id = models.CharField(max_length=32, null=True)
    file_num = models.BigIntegerField(null=True)
    memo_cd = models.CharField(max_length=1, null=True)
    memo_text = models.CharField(max_length=100, null=True)
    sub_id = models.BigIntegerField(null=True)
    
    


