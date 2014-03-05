from django.contrib import admin
from models import District, Candidate_Overlay
#Election, Election_Candidate, SubElection

class DistrictAdmin(admin.ModelAdmin):
    
    fieldsets = (
        ("Human-verified data", {
            'fields': ('next_election_date','next_election_code', 'special_election_scheduled', 'open_seat', 'district_notes'),
        }),
        ("From FEC", {
            'fields': ('cycle','state', 'office', 'office_district', 'incumbent_name', 'incumbent_pty', 'incumbent_party', 'election_year'),
                   
        }),
    )
    search_fields=['incumbent_name', 'state']
    list_display=['office', 'state', 'incumbent_name', 'office_district', 'term_class']
admin.site.register(District, DistrictAdmin) 
    
    
class Candidate_OverlayAdmin(admin.ModelAdmin):
    readonly_fields = ('fec_id', 'pcc')
    fieldsets = (
        ("Human-curated data", {
            'fields': ('curated_election_year', 'other_office_sought', 'other_fec_id', 'not_seeking_reelection', 'bio_blurb', 'display', 'is_minor_candidate', 'is_incumbent', 'name'),
            
        }),
        ("Mostly autopopulated", {
            'fields': ('cycle','district', 'party', 'fec_id', 'pcc', 'election_year', 'state','office', 'office_district', 'cand_ici', 'candidate_status'),
                   
        }),
        

    )
    search_fields=['name', 'state']
    
admin.site.register(Candidate_Overlay, Candidate_OverlayAdmin)

"""
class ElectionAdmin(admin.ModelAdmin):
    
    fieldsets = (
        ("Human-verified data", {
            'fields': ('open_seat',),
            
        }),
        ("Mostly autopopulated", {
            'fields': ('election_code', 'incumbent_name','incumbent_party', 'election_year', 'state', 'term_class','office', 'office_district'),
                   
        }),
        
    )
    search_fields=['incumbent_name', 'state']
    
admin.site.register(Election, ElectionAdmin)

# For SubElectionAdmin class, if needed
# 'primary_party', 'primary_contested', 'election_date','election_voting_start_date', 'election_voting_end_date',

class SubElectionAdmin(admin.ModelAdmin):
    
    fieldsets = (
        ("Human-verified data", {
            'fields': ('election_date','election_voting_start_date', 'election_voting_end_date'),
            
        }),
        ("Mostly autopopulated", {
            'fields': ('subelection_code', 'primary_party', 'is_contested'),
                   
        }),
        
    )
    search_fields=['incumbent_name', 'state']
    
admin.site.register(SubElection, SubElectionAdmin)


class Election_CandidateAdmin(admin.ModelAdmin):
    readonly_fields = ('candidate','race')
    fieldsets = (
        ("Autopopulated", {
            'fields': ('candidate', 'race'),
                   
        }),
        ("Non-fec data", {
            'fields': ('is_sole_winner','advance_to_runoff', 'is_loser', 'vote_percent', 'vote_number'),
            
        }),
        
    )
    search_fields=['candidate']
    
admin.site.register(Election_Candidate, Election_CandidateAdmin)

"""
