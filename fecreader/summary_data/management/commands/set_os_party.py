""" Set party leaning for outside spending groups. Better version will take into account primary spending. Not sure that's needed. """

from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from formdata.models import SkedE
from summary_data.models import Candidate_Overlay, Committee_Overlay



class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        # Leave out committees we've verified by hand
        committee_list = Committee_Overlay.objects.filter(total_indy_expenditures__gte=1000).exclude(political_orientation_verified=True)
        for committee in committee_list:
            if committee.ie_support_dems > 0 and not committee.ie_support_reps > 0:
                committee.political_orientation = 'D'
                print "Supports only Ds %s" % (committee.name)
                committee.save()                
            elif committee.ie_support_reps > 0 and not committee.ie_support_dems > 0:
                committee.political_orientation = 'R'
                print "Supports only Rs %s" % (committee.name)
                committee.save()
            
            # if they've only spend negatively, they might just be playing in the primary. 
            elif committee.ie_oppose_reps > 0 and not committee.ie_oppose_dems > 0 and not committee.ie_support_reps > 0 and not committee.ie_support_dems > 0:
                print "Purely negative againsts Rs -- not setting. %s" % (committee.name)
            
            # if they've only spend negatively, they might just be playing in the primary. 
            elif not committee.ie_oppose_reps > 0 and committee.ie_oppose_dems > 0 and not committee.ie_support_reps > 0 and not  committee.ie_support_dems > 0:
                print "Purely negative againsts Ds -- not setting. %s" % (committee.name)
            else:
                print "***** Other. %s" % (committee.name)
        
        