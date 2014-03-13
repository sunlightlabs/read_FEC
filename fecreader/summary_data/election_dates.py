from datetime import date as d

# these are the base election dates; the general election is 11/4/2014; georgia and lousiana have runoffs
#But there are modifications... 
# to be clear the runoffs are primary runoffs. 
# Louisiana holds it's primary on general election day, and there is no general unless no gets 50% of the vote
# Or maybe  
election_dates_2014 = {
    'AL': {'runoff': d(2014, 7, 15), 'primary': d(2014, 6, 3), 'has_runoff': '1'},
    'TX': {'runoff': d(2014, 5, 27), 'primary': d(2014, 3, 4), 'has_runoff': '1'},
    'IL': {'runoff': '', 'primary': d(2014, 3, 18), 'has_runoff': '0'},
    'DC': {'runoff': '', 'primary': d(2014, 4, 1), 'has_runoff': '0'},
    'IN': {'runoff': '', 'primary': d(2014, 5, 6), 'has_runoff': '0'},
    'NC': {'runoff': d(2014, 7, 15), 'primary': d(2014, 5, 6), 'has_runoff': '1'},
    'OH': {'runoff': '', 'primary': d(2014, 5, 6), 'has_runoff': '0'},
    'NE': {'runoff': '', 'primary': d(2014, 5, 13), 'has_runoff': '0'},
    'WV': {'runoff': '', 'primary': d(2014, 5, 13), 'has_runoff': '0'},
    'AR': {'runoff': d(2014, 6, 10), 'primary': d(2014, 5, 20), 'has_runoff': '1'},
    'GA': {'runoff': d(2014, 7, 22), 'primary': d(2014, 5, 20), 'has_runoff': '1'},
    'ID': {'runoff': '', 'primary': d(2014, 5, 20), 'has_runoff': '0'},
    'KY': {'runoff': '', 'primary': d(2014, 5, 20), 'has_runoff': '0'},
    'OR': {'runoff': '', 'primary': d(2014, 5, 20), 'has_runoff': '0'},
    'PA': {'runoff': '', 'primary': d(2014, 5, 20), 'has_runoff': '0'},
    'CA': {'runoff': '', 'primary': d(2014, 6, 3), 'has_runoff': '0'},
    'IA': {'runoff': '', 'primary': d(2014, 6, 3), 'has_runoff': '0'},
    'MS': {'runoff': d(2014, 6, 24), 'primary': d(2014, 6, 3), 'has_runoff': '1'},
    'MT': {'runoff': '', 'primary': d(2014, 6, 3), 'has_runoff': '0'},
    'NJ': {'runoff': '', 'primary': d(2014, 6, 3), 'has_runoff': '0'},
    'NM': {'runoff': '', 'primary': d(2014, 6, 3), 'has_runoff': '0'},
    'SD': {'runoff': d(2014, 8, 12), 'primary': d(2014, 6, 3), 'has_runoff': '1'},
    'ME': {'runoff': '', 'primary': d(2014, 6, 10), 'has_runoff': '0'},
    'NV': {'runoff': '', 'primary': d(2014, 6, 10), 'has_runoff': '0'},
    'ND': {'runoff': '', 'primary': d(2014, 6, 10), 'has_runoff': '0'},
    'SC': {'runoff': d(2014, 6, 24), 'primary': d(2014, 6, 10), 'has_runoff': '1'},
    'VA': {'runoff': '', 'primary': d(2014, 6, 10), 'has_runoff': '0'},
    'CO': {'runoff': '', 'primary': d(2014, 6, 24), 'has_runoff': '0'},
    'MD': {'runoff': '', 'primary': d(2014, 6, 24), 'has_runoff': '0'},
    'NY': {'runoff': '', 'primary': d(2014, 6, 24), 'has_runoff': '0'},
    'OK': {'runoff': d(2014, 8, 26), 'primary': d(2014, 6, 24), 'has_runoff': '1'},
    'UT': {'runoff': '', 'primary': d(2014, 6, 24), 'has_runoff': '0'},
    'VI': {'runoff': '', 'primary': d(2014, 8, 2), 'has_runoff': '0'},
    'KS': {'runoff': '', 'primary': d(2014, 8, 5), 'has_runoff': '0'},
    'MI': {'runoff': '', 'primary': d(2014, 8, 5), 'has_runoff': '0'},
    'MO': {'runoff': '', 'primary': d(2014, 8, 5), 'has_runoff': '0'},
    'WA': {'runoff': '', 'primary': d(2014, 8, 5), 'has_runoff': '0'},
    'TN': {'runoff': '', 'primary': d(2014, 8, 7), 'has_runoff': '0'},
    'HI': {'runoff': '', 'primary': d(2014, 8, 9), 'has_runoff': '0'},
    'CT': {'runoff': '', 'primary': d(2014, 8, 12), 'has_runoff': '0'},
    'MN': {'runoff': '', 'primary': d(2014, 8, 12), 'has_runoff': '0'},
    'WI': {'runoff': '', 'primary': d(2014, 8, 12), 'has_runoff': '0'},
    'AK': {'runoff': '', 'primary': d(2014, 8, 19), 'has_runoff': '0'},
    'WY': {'runoff': '', 'primary': d(2014, 8, 19), 'has_runoff': '0'},
    'AZ': {'runoff': '', 'primary': d(2014, 8, 26), 'has_runoff': '0'},
    'FL': {'runoff': '', 'primary': d(2014, 8, 26), 'has_runoff': '0'},
    'VT': {'runoff': '', 'primary': d(2014, 8, 26), 'has_runoff': '0'},
    'GU': {'runoff': '', 'primary': d(2014, 8, 30), 'has_runoff': '0'},
    'DE': {'runoff': '', 'primary': d(2014, 9, 9), 'has_runoff': '0'},
    'MA': {'runoff': '', 'primary': d(2014, 9, 9), 'has_runoff': '0'},
    'NH': {'runoff': '', 'primary': d(2014, 9, 9), 'has_runoff': '0'},
    'RI': {'runoff': '', 'primary': d(2014, 9, 9), 'has_runoff': '0'},
    'LA': {'runoff': '', 'primary': '', 'has_runoff': '0'}
}

# ELECTION_TYPE_CHOICES = (('G', 'General'), ('P', 'Primary'), ('PR', 'Primary Runoff'), ('GR', 'General Runoff'), ('SP', 'Special Primary'), ('OR', 'Special Primary Runoff'), ('SG', 'Special General'), ('SR', 'Special General Runoff'), ('O', 'Other'))

# LA has general runoffs; the missouri special didn't have a primary ?  
special_house_elections = [
    {'state':'FL', 'district':'13', 'elections': {'P': d(2014,1,14), 'G':d(2014,3,11) }},
    {'state':'FL', 'district':'19', 'elections': {'P': d(2014,4,22), 'G':d(2014,6,24) }},
    {'state':'NC', 'district':'12', 'elections': {'P': d(2014,5,6), 'G':d(2014,11,4), 'PR': d(2014,7,15) }},
    {'state':'NJ', 'district':'01', 'elections': {'P': d(2014,6,3), 'G':d(2014,11,4) }},
    {'state':'AL', 'district':'01', 'elections': {'P': d(2013,9,24), 'G':d(2013,12,17), 'PR':d(2013,11,5) }},
    {'state':'IL', 'district':'02', 'elections': {'P': d(2013,2,26), 'G':d(2013,4,9) }},
    {'state':'LA', 'district':'05', 'elections': {'P': d(2013,8,21), 'G':d(2013,10,19), 'GR':d(2013,11,16) }},
    {'state':'MA', 'district':'05', 'elections': {'P': d(2013,10,15), 'G':d(2013,12,10) }},
    {'state':'MO', 'district':'08', 'elections': {'G': d(2013,6,4) }},
    {'state':'SC', 'district':'01', 'elections': {'P': d(2013,6,3), 'G':d(2013,5,7), 'PR':d(2013,4,2) }}
]

special_senate_elections = [
    {'state':'OK', 'term_class':'3', 'elections': {'P': d(2014,6,24), 'G':d(2014,11,4), 'SR':d(2014,8,26) }},
    {'state':'MA', 'term_class':'2', 'elections': {'P': d(2013,5,30), 'G':d(2013,6,25) }},
    {'state':'NJ', 'term_class':'2', 'elections': {'P': d(2013,8,13), 'G':d(2013,10,16) }}
]



