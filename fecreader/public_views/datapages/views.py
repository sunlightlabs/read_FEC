import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection

from race_curation.utils.senate_crosswalk import senate_crosswalk
from fec_alerts.models import new_filing, newCommittee

# get not null senate ids. 
senate_ids =  [ senator['fec_id'] for senator in senate_crosswalk if senator['fec_id'] ]

def current_senators(request):

    title="Senate Fundraising Summary"
    explanatory_text="Quarterly fundraising totals are based on money raised and spent by a legislator's principal campaign committee. Money raised by a leadership PAC is not included, unless it was transferred to a principal campaign committee during this period "

    # Give up on ORM for data; we're not willing to enforce all the relationships required for them
    
    cursor = connection.cursor()

    subquery = """(select fec_id from race_curation_candidate_overlay where cand_ici = 'I' and office = 'S';)"""
    cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
    row = cursor.fetchone()
    
    return render_to_response('datapages/legislator_list.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        }
    )

def newest_filings(request):
    
    filings = new_filing.objects.all().order_by('-filing_number')[:50]
    title="Newest filings"
    explanatory_text="These are the most recent electronic filings received. Senate candidates, and certain senate committees, are still allowed to file on paper."
    
    return render_to_response('datapages/filing_list.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'object_list':filings,
        }
    )
    
def new_committees(request):
    today = datetime.datetime.today()
    month_ago = today - datetime.timedelta(days=30)
    committees=newCommittee.objects.filter(date_filed__gte=month_ago).order_by('-date_filed')
    return render_to_response('datapages/new_committees.html', {
                'object_list':committees,
                'explanatory_text':'These are committees formed within the last 30 days. It may take several days after a PAC is formed for details to be posted.',
                'title':'New Committees'
                })

def downloads(request):
    
    return render_to_response('datapages/downloads.html', {
        'title':'Downloads'
                })




    