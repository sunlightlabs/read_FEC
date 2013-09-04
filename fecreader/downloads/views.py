import json

from celeryproj.tasks import add
from celery.result import AsyncResult

from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render_to_response

from reconciliation.utils.json_helpers import render_to_json, render_to_json_via_template

def get_filing(request, filing_number, sked):
    # should eventually have a home page, or straighten out urls
    b = add.apply_async([1,2], queue='slow',routing_key="slow")
    print "stating task %s %s %s" % (b.id, b.state, b.result)
    
    task_id = b.id
    return redirect('/download/build_file/%s/' % task_id)
    
def build_file(request, task_id):
    # this is the page that gets shown while the file is downloading. It polls the status until it's done. 
    
    return render_to_response('downloads/build_file.html',
        {
        'task_id':task_id,
        })
    
def get_task_status(request, task_id):

    result = AsyncResult(task_id)
    return_obj = {}
    if result.state == 'SUCCESS':
        return_obj = {'done':True, 'result':result.result}
    else:
        return_obj = {'done':False, 'result':None}
        
    return render_to_json(json.dumps(return_obj))

