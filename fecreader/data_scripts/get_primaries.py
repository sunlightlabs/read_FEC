# How many incumbents have credible challengers? 
import sys, os

from django.core.management import setup_environ
sys.path.append('../fecreader/')
sys.path.append('../')

import settings
setup_environ(settings)

from summary_data.models import District, Candidate_Overlay

fundraising_threshold = 100000

for office in ['H']:
    # Ignore open seats
    races = District.objects.filter(office=office, open_seat=False).order_by('incumbent_party')

    for race in races:
        incumbent_party = race.incumbent_party
        primary_challengers = Candidate_Overlay.objects.filter(district=race, is_incumbent=False, party=incumbent_party, total_receipts__gte=fundraising_threshold).exclude(not_seeking_reelection=True)
        if primary_challengers:
            print "\n\nFound credible challenger to %s (%s) - rating: %s - %s %s %s" % (race.incumbent_name, race.incumbent_party, race.rothenberg_rating_text ,race.state, race.office, race.office_district)
            for challenger in primary_challengers:
                print "\tchallenger: %s (%s) total raised: %s cash on hand %s (as of %s)" % (challenger.name, challenger.party, challenger.total_receipts, challenger.cash_on_hand, challenger.cash_on_hand_date )
