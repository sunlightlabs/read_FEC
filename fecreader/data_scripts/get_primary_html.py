# How many incumbents have credible challengers? 
import sys, os

from django.core.management import setup_environ
sys.path.append('../fecreader/')
sys.path.append('../')

import settings
setup_environ(settings)

from summary_data.models import District, Candidate_Overlay

from django.contrib.humanize.templatetags import humanize
# humanize.intcomma('42000')

fundraising_threshold = 100000

def print_candidate_details(candidate, is_incumbent=False):
    returnstring = ""
    if (is_incumbent):
        returnstring += "<b>Incumbent: </b>"
    returnstring += """<a href="http://realtime.influenceexplorer.com%s">%s (%s)</a>Total raised: $%s  Cash on hand: $%s (as of %s) """ % (candidate.get_absolute_url(), candidate.name, candidate.party,  humanize.intcomma(candidate.total_receipts), humanize.intcomma(candidate.cash_on_hand), candidate.cash_on_hand_date.strftime("%m/%d"))
    return "<li>" + returnstring + "</li>"
        
def print_district(district):
    returnstring = ""
    
    returnstring += """<b><a href="http://realtime.influenceexplorer.com%s">House District %s-%s</a></b>""" % (district.get_absolute_url(), district.state, district.office_district)
    
    if district.incumbent_party =='R':
        returnstring += " (Republican) "
    elif district.incumbent_party =='D':
        returnstring += " (Democratic) "
        
    returnstring += " Rothenberg rating: %s""" % (race.rothenberg_rating_text)
    
    return returnstring 


for office in ['H']:
    # Ignore open seats
    races = District.objects.filter(office=office, open_seat=False).order_by('incumbent_party', 'state')

    for race in races:
        incumbent_party = race.incumbent_party
        primary_challengers = Candidate_Overlay.objects.filter(district=race, is_incumbent=False, party=incumbent_party, total_receipts__gte=fundraising_threshold).exclude(not_seeking_reelection=True)
        if primary_challengers:
            #print "\n\nFound credible challenger to %s (%s) - rating: %s - %s %s %s" % (race.incumbent_name, race.incumbent_party, race.rothenberg_rating_text ,race.state, race.office, race.office_district)
            print print_district(race) 
            print "<ul>"
            try:
                incumbent = Candidate_Overlay.objects.filter(district=race, is_incumbent=True)[0]
                print print_candidate_details(incumbent, True)
            except:
                #print "**missing incumbent data"
                pass
            
            for challenger in primary_challengers:
                print print_candidate_details(challenger)
            print "</ul>"
            print "<p>Text goes here!</p><hr>"
