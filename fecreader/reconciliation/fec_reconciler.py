from fuzzywuzzy import fuzz
import jellyfish
import unicodedata, pickle
from reconciliation.utils.matchlength import longest_match
from django.db.models import Q
from ftpdata.models import Candidate
from nameparser import HumanName
from datetime import date
from operator import itemgetter
from reconciliation.utils.candidate_aliases import candidate_hash

from django.conf import settings

from reconciliation.utils.nicknames import nicknamedict

import logging
log = logging.getLogger('reconcilers')



CHECK_FOR_NAME_REVERSALS = getattr(settings, 'CHECK_FOR_NAME_REVERSALS')

# alias table has this format. 
#candidate_hash = {'2014': {'JACK, JACK': {'cand_name': u'JACK, JACK', 'cand_office': u'H', 'cand_office_district': u'06', 'cand_id': 'H8CO06138', 'cand_pty_affiliation': u'REP', 'cand_office_st': u'CO'}}}


#push to settings?
default_cycle='2016'

# Log to the log file ? 
debug=True
starts_with_blocklength = 5

# standardize the name that gets passed back to refine - add details to help id the candidate
def standardize_name_from_dict(candidate):
    district = ""
    if candidate['cand_office'] != '00':
        district = "-%s" % candidate['cand_office_district']
    return "%s - %s (%s: %s-%s)" % (candidate['cand_name'], candidate['cand_pty_affiliation'], candidate['cand_office'], candidate['cand_office_st'], district)

# We should have been given a last name to block with. We should probably block by
# something less restrictive (this fails on incorrectly formatted names, i.e. "ron, 
# paul") but... 
# cycle must match a string, not an int, eventually 
def block_by_startswith(name, numchars, state=None, office=None, cycle=None):
    namestart = name[:numchars]
    if debug:
        log.debug("block_by_startswith = %s state=%s office=%s cycle=%s" % (name, state,office, cycle))
    print("block_by_startswith = %s state=%s office=%s cycle=%s" % (name, state,office, cycle))
        
    matches = Candidate.objects.filter(cand_name__istartswith=namestart)
    president_flag = False
    if office:
        if office.upper()[:1] == 'H':
            matches = matches.filter(cand_office='H')
        elif office.upper()[:1] == 'S':
            matches = matches.filter(cand_office='S')
        elif office.upper()[:1] == 'P':
            matches = matches.filter(cand_office='P')
            president_flag = True        
        
    if state and not president_flag:
        state = state.strip().upper()
        matches = matches.filter(cand_office_st=state)
    
    # default to the current year; this will break for the house between jan. 1 and whenever folks are sworn in, usually jan. 3, I think... 
    if cycle and len(str(cycle)) > 3:
        matches = matches.filter(cycle=cycle)
    
    matches = matches.order_by('cand_name', 'cand_office', 'cand_office_st', 'cand_office_district', 'cand_id', 'cand_pty_affiliation')
    match_values = matches.values('cand_name', 'cand_office', 'cand_office_st', 'cand_office_district', 'cand_id', 'cand_pty_affiliation').distinct()

    #print "result is %s" % match_values
    return match_values

def simple_clean(string):
    try:
        string = unicodedata.normalize('NFKD',string).encode('ascii','ignore')
    except TypeError:
        pass
        #log.error("unicode typeerror!")
    return string.strip().lower()

# throw out the lowest one and calculate an average. 
def compute_scores(array):
    sorted_array = sorted(array)
    truncated = sorted_array[1:]
    avg = sum(truncated) / float(len(truncated))
    return avg

def unnickname(firstname):
    firstname = simple_clean(firstname)
    try:
        firstname = nicknamedict[firstname]
    except KeyError:
        pass
    return firstname

def hash_lookup(name, state=None, office=None, cycle=None):
    result_array = []
    print "1. running hash lookup with name='%s' and cycle='%s' and state='%s' office='%s'" % (name, cycle, state, office)
    # try to short circuit with the alias table. For now we're using a default cycle--but maybe we should only do this when a cycle is present ?
    # Again, cycle is a string. 
    hashname = str(name).upper().strip().strip('"')
    print "Hash lookup name = %s" % (hashname)
    if cycle and len(str(cycle)) > 3:
        hash_lookup_cycle = str(cycle)
    else:
        hash_lookup_cycle = default_cycle
        
    # Our lookup hash is only for 2012 for now, so... 
    # This doesn't address bootstrapping 2012 lookups for 2014...

    ### Need to cleanly remove this logic for multicycle
    if hash_lookup_cycle==default_cycle:
        
        try:
            found_candidate = candidate_hash[hash_lookup_cycle][hashname]
        except KeyError:
            return None
        if found_candidate:
            valid_candidate = True
            
            # If we have additional identifiers, insure that they're right. 
            if office and len(office) > 0:
                if office.upper()[:1] != found_candidate['cand_office'].upper()[:1]:
                    valid_candidate = False
            
            # ignore states for president.
            if state and len(state) > 1:
                if state.upper() != found_candidate['cand_office_st']:
                    if office and office.upper()[:1] == 'P':
                        pass
                    else:
                        valid_candidate = False
                    
            if valid_candidate:
                name_standardized = standardize_name_from_dict(found_candidate)
                
                result_array.append({'name':name_standardized, 'id':found_candidate['cand_id'], 'score':1, 'type':[], 'match':True})
                return result_array
    return None


def match_by_name(name, state=None, office=None, cycle=None, reverse_name_order=False):
    result_array = []
    name1 = HumanName(name)
    
    name1_standardized = None
    blocking_name = None
    
    # sometimes we run into a name that's flipped:
    if reverse_name_order:
        print "Running name reversal check!"
        blocking_name = simple_clean(name1.first)
        name1_standardized = simple_clean(name1.first) + " " + unnickname(name1.last)
    
    else:
        name1_standardized = simple_clean(name1.last) + " " + unnickname(name1.first)
        blocking_name = simple_clean(name1.last)
    
    # if we can't find the last name, assume the name is the last name. This might be a bad idea. 
    if not blocking_name:
        blocking_name = simple_clean(name)
        
    possible_matches = block_by_startswith(blocking_name, starts_with_blocklength, state, office, cycle)
        
    for match in possible_matches:
        
        name2_name = HumanName(match['cand_name'])
        name2 = simple_clean(name2_name.last) + " " + unnickname(name2_name.first)
        # calculate a buncha metrics
        text1 = name1_standardized
        text2 = name2
        #print "comparing '%s' to '%s'" % (text1, text2)
        ratio = 1/100.0*fuzz.ratio(text1, text2)
        partial_ratio = 1/100.0*fuzz.partial_ratio(text1, text2)
        token_sort_ratio = 1/100.0*fuzz.token_sort_ratio(text1, text2)
        token_set_ratio = 1/100.0*fuzz.token_set_ratio(text1, text2)
        
        avg_len = 1/2*len(text1)+len(text2)
        min_len = min(len(text1), len(text2))
        
        l_ratio = 0
        try:
            l_distance = jellyfish.levenshtein_distance(text1, text2)
            l_ratio = 1.0 - ( (0.0 + l_distance) / (0.0+avg_len) )
        except UnicodeEncodeError:
            pass
            
        long_match = longest_match(text1, text2)
        lng_ratio = (0.0 + long_match) / (0.0 + min_len)
        
        score = 0
        if ( ratio > 0.6 or partial_ratio > 0.6 or l_ratio > 0.6 or lng_ratio > 0.6):
            score = compute_scores([ratio,partial_ratio,l_ratio,lng_ratio])
           
        if debug:
            log.debug("|fuzzymatchresult|%s|'%s'|'%s'|score=%s|ratio=%s|partial_ratio=%s|token_sort_ratio=%s|token_set_ratio=%s| l_ratio=%s|lng_ratio=%s" % (match['cand_id'], match['cand_name'], name, score, ratio, partial_ratio, token_sort_ratio, token_set_ratio, l_ratio, lng_ratio))
        
        
        if (score > 0.8):
            name_standardized = standardize_name_from_dict(match)
            result_array.append({'name':name_standardized, 'id':match['cand_id'], 'score':score, 'type':[], 'match':False})
            if debug:
                log.debug("Match found: %s" % name_standardized)
    
    if debug and len(result_array)==0:
        log.debug("No match for %s, which was standardized to: %s" % (name, name1_standardized))
            
    # If it's a good match and there's only one, call it a definite match.
    if (len(result_array)==1):
        if result_array[0]['score'] > 0.9:
            result_array[0]['match'] = True        
    # surprisingly, google refine *doesn't* sort by score.
    return result_array

def run_fec_query(name, state=None, office=None, cycle=None, fuzzy=True):
    if debug:
        print "run_fec_query = state=%s office=%s cycle=%s" % (state,office, cycle)
        
    result = hash_lookup(name, state, office, cycle)
    if result:
        return result
    if not fuzzy:
        return []
    
    # don't even bother if there are less than 4 letters 
    if (len(name) < 4):
        return []
    
    result_array = match_by_name(name, state=state, office=office, cycle=cycle, reverse_name_order=False)
    
    # If there are no matches, maybe the name got flipped? 
    if CHECK_FOR_NAME_REVERSALS and len(result_array)==0:
        result_array = match_by_name(name, state=state, office=office, cycle=cycle, reverse_name_order=True)
    
    result_array = sorted(result_array, key=itemgetter('score'), reverse=True)
    return result_array
        
