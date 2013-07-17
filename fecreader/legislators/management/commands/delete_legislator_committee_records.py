from django.core.management.base import BaseCommand, CommandError

from legislators.models import *



class Command(BaseCommand):
    help = "Dump all us congress data"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        Legislator.objects.all().delete()
        fec.objects.all().delete()
        Other_Names.objects.all().delete()
        Term.objects.all().delete()
        Committee.objects.all().delete()
        CurrentCommitteeMembership.objects.all().delete()
        