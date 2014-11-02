from django.contrib import admin
from models import District, Candidate_Overlay, Committee_Overlay, ElectionSummary

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
            'fields': ('name', 'cand_is_gen_winner', 'is_general_candidate', 'curated_election_year', 'candidate_status', 'other_office_sought', 'other_fec_id', 'not_seeking_reelection', 'is_incumbent'),
            
        }),
        ("Mostly autopopulated", {
            'fields': ('cycle','district', 'party', 'fec_id', 'pcc', 'election_year', 'state','office', 'office_district', 'cand_ici'),
                   
        }),
        

    )
    search_fields=['name', 'state']
    
admin.site.register(Candidate_Overlay, Candidate_OverlayAdmin)

class ElectionSummaryAdmin(admin.ModelAdmin):
    
    fieldsets = (
        ("Human-verified data", {
            'fields': ('election_winner','primary_runoff_needed', 'general_runoff_needed'),
        }),
    )
    search_fields=['district__incumbent_name']

admin.site.register(ElectionSummary, ElectionSummaryAdmin)

class Committee_OverlayAdmin(admin.ModelAdmin):
    readonly_fields = ('name','designation', 'ctype')
    ordering = ('name',)
    
    fieldsets = (
    ("Autopopulated", {
        'fields': ('name', 'designation','ctype'),
               
    }),
        ("Human-verified data", {
            'fields': ('political_orientation','political_orientation_verified', 'org_status'),
        }),
    )
    search_fields=['name']
    list_display=['name', 'ctype', 'designation',]
    

admin.site.register(Committee_Overlay, Committee_OverlayAdmin)
