import json, re
from reconciliation.utils.json_helpers import render_to_json, render_to_json_via_template
from reconciliation.fec_reconciler import run_fec_query
from django.views.decorators.csrf import csrf_exempt 
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404, render_to_response
from django.http import Http404

from ftpdata.models import Candidate



try:
    PREVIEW_BASE_URL = settings.PREVIEW_BASE_URL
    PREVIEW_WIDTH = settings.PREVIEW_WIDTH
    PREVIEW_HEIGHT = settings.PREVIEW_HEIGHT
except:
    raise Exception("Couldn't import preview settings. Are PREVIEW_BASE_URL, PREVIEW_WIDTH and PREVIEW_HEIGHT defined in a settings file?")

# Return the service metadata 
def get_metadata(callbackarg, reconciliation_type):
    
    reconciliation_name = 'sunlight reporting reconcile 0.1'
    PREVIEW_BASE = ""
    if (reconciliation_type=='fec_ids' or reconciliation_type == 'fec_ids_nofuzzy'):
        reconciliation_name = 'fec id matcher - no fuzzy lookups 0.1'
        if (reconciliation_type=='fec_ids'):
            reconciliation_name = 'fec id matcher 0.1'            
        PREVIEW_BASE = PREVIEW_BASE_URL % ('fec_ids')
        
    else:
        return Http404
    """
    elif (reconciliation_type=='legislators'):
        reconciliation_name = 'legislators matcher 0.1'
        PREVIEW_BASE = PREVIEW_BASE_URL % ('legislators')
    """
    
    # setting the URL to the preview...
    return render_to_json_via_template("reconciliation/service_metadata.json", {
        'space_base':"http://reporting.sunlightfoundation.com/",
        'url_base':PREVIEW_BASE,
        'preview_base':PREVIEW_BASE,
        'reconciliation_name':reconciliation_name, 
        'callbackarg':callbackarg,
        'preview_width':PREVIEW_WIDTH,
        'preview_height':PREVIEW_HEIGHT
    })

def normalize_properties(query):
    # properties can use either 'p' or 'pid'; 'pid' seems to be a throwback to freebase and won't be used here. Convert all pid's or p's to keys
    properties = query.get('properties')
    if not properties:
        return None
    newprop_array = []
    for this_prop in properties:
        try:
            this_prop['pid']
            newprop_array.append({this_prop['pid']:this_prop['v']})
        except KeyError:
            newprop_array.append({this_prop['p']:this_prop['v']})
            
    #print "properties are: %s" % newprop_array
    return newprop_array
    
def flatten_properties(query):
    # properties can use either 'p' or 'pid'; 'pid' seems to be a throwback to freebase and won't be used here. Convert all pid's or p's to keys
    properties = query.get('properties')
    if not properties:
        return query
    for this_prop in properties:
        try:
            this_prop['pid']
            newprop_array.append({this_prop['pid']:this_prop['v']})
        except KeyError:
            newprop_array.append({this_prop['p']:this_prop['v']})

    #print "properties are: %s" % newprop_array
    return newprop_array


    
def do_fec_query(query, fuzzy=True):
    #print "running query: %s" % (query['query'])
    properties = normalize_properties(query)
    #print "running query with properties=%s" % (properties)
    state = None
    office = None
    cycle = None
    if properties:
        for thisproperty in properties:
            for key in thisproperty:
                if key=='state':
                    state = thisproperty['state']
                elif key =='office':
                    office = thisproperty['office']
                elif key =='cycle':
                    cycle = thisproperty['cycle']
    match_key_hash = run_fec_query(query['query'], state=state, office=office, cycle=cycle, fuzzy=fuzzy)
    return match_key_hash

    


def do_query(query, reconciliation_type):
    if reconciliation_type == 'legislators':
        return do_legislator_query(query)
    elif reconciliation_type == 'fec_ids':
        return do_fec_query(query, fuzzy=True)
    elif reconciliation_type == 'fec_ids_nofuzzy':
        return do_fec_query(query, fuzzy=False)
    else:
        raise Exception ("Invalid reconciliation type: %s" % (reconciliation_type))

@csrf_exempt
def refine(request, reconciliation_type):
    
    #print "request is: %s" % (request)    
    # spec is to return metadata for any callback arg. 
    if request.REQUEST.get('callback'):
        callbackarg = request.REQUEST.get('callback')
        return get_metadata(callbackarg, reconciliation_type)
        
    query = request.REQUEST.get('query')
    queries = request.REQUEST.get('queries')

    result = {}
    if query:
        print "query is: %s" % query
        # Spec allows a simplified version, i.e. ?query=boston, so check for that first. 
        # ?query={"query":"boston","type":"/music/musical_group"}
        # ?query={"query":"Ford Taurus","limit": 3,"type":"/automotive/model","type_strict":"any","properties": [{"p":"year","v": 2009},{"pid":"/automotive/model/make","v":{"id":"/en/ford"}} ]}
        # !!This means using the word 'query' in an abbreviated search will break !! 
        if not re.search('query', query):
            query = "{\"query\":\"%s\"}" % query
            #print "revised query is: %s" % query
        
        q = json.loads(query)
        result  = do_query(q, reconciliation_type)
        #print "\n" + str(result)
        thisjson={}
        thisjson['result'] = result
        #print "this json = %s" % thisjson
        return render_to_json(json.dumps(thisjson))
        
    elif queries:
        #print "queries is %s" % queries
        # ?queries={ "q0" : { "query" : "hackney" }, "q1" : { "query" : "strategic" } }
        q = json.loads(queries)
        thisjson={}
        if q is not None:

            for key, query in q.iteritems():
                
                result  = do_query(query, reconciliation_type)
                #print "\n" + str(result)
                thisjson[key] = {'result':result}
                
        #print "this json: %s" % thisjson
        return render_to_json(json.dumps(thisjson))
        
    else:
        message = "Couldn't decode the query JSON!"
        return render_to_json("{'Error':'%s'}" % message)
    
# pass url-encoded json that's not quite so weird.
# instead of using:
# {"q0":{"query":"runyan, jon","type":"","type_strict":"should","properties":[{"pid":"state","v":"NJ"}]},"q1":{"query":"Romney, Mitt","type":"","type_strict":"should","properties":[{"pid":"state","v":""}]}}
# use: 
# {"q0":{"query":"runyan, jon","state":"NJ"}, "q1":{"query":"Romney, Mitt","state":"", "cycle":"2012"}} 
@csrf_exempt
def refine_json(request, reconciliation_type):
    
    fuzzy=True
    if reconciliation_type == 'fec_ids':
        pass
    elif reconciliation_type == 'fec_ids_nofuzzy':
        fuzzy=False
    else:
        raise Exception ("Invalid reconciliation type: %s" % (reconciliation_type))
    
    queries = request.REQUEST.get('queries')
    if queries:
        q = json.loads(queries)
        thisjson={}
        if q is not None:
            for key, query in q.iteritems():
                
                state = query.get('state', None)
                office = query.get('office', None)
                cycle = query.get('cycle', None)
                result = run_fec_query(query['query'], state=state, office=office, cycle=cycle, fuzzy=fuzzy)
                thisjson[key] = {'result':result}
        return render_to_json(json.dumps(thisjson))

        
    else:
        message = "Couldn't decode the query JSON!"
        return render_to_json("{'Error':'%s'}" % message)




def preview(request, fec_id):
    candidates = Candidate.objects.filter(cand_id=fec_id).order_by('-cycle')
    try:
        candidate = candidates[0]
    except IndexError:
        raise Http404
    return render_to_response('reconciliation/fec_preview.html', 
       {
       'candidate':candidate,
       'candidates':candidates,
       'preview_height':PREVIEW_HEIGHT - 30,
       'preview_width':PREVIEW_WIDTH - 20
       })
