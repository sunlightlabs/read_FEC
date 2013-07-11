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


def newest_filings_template(request, filings, explanatory_text, title):
        explanatory_text = explanatory_text + "<br>See also:&nbsp; <a href=\"/newest-filings/ies/\">independent expenditure filings</a>&nbsp;|&nbsp;<a href=\"/newest-filings/candidates/\">declaration of candidacy</a>&nbsp;|&nbsp;<a href=\"/newest-filings/\">newest filings</a>"
        return render_to_response('datapages/filing_list.html',
            {
            'title':title,
            'explanatory_text':explanatory_text,
            'object_list':filings,
            }
        )
            


def newest_filings(request):
    filings = new_filing.objects.all().order_by('-filing_number')[:100]
    title="Newest filings"
    explanatory_text="These are the 100 most recent electronic filings received. Senate candidates, and certain senate committees, are still allowed to file on paper."
    return newest_filings_template(request, filings, explanatory_text, title)
"""
Haven't started setting this flag yet... 

def newest_filings_superpacs(request):
    filings = new_filing.objects.filter(is_superpac=True).order_by('-filing_number')[:100]
    title="Newest filings"
    explanatory_text="These are the 100 most recent electronic filings received. Senate candidates, and certain senate committees, are still allowed to file on paper."
    return newest_filings_template(request, filings, explanatory_text, title)
"""

def newest_filings_ies(request):
    filings = new_filing.objects.filter(form_type__in=['F5A', 'F5N', 'F24A', 'F24N']).order_by('-filing_number')[:100]
    title="Newest Independent Expenditure filings"
    explanatory_text="These are the 100 most recent independent expenditure electronic filings received."
    return newest_filings_template(request, filings, explanatory_text, title)

def newest_filings_candidates(request):
    filings = new_filing.objects.filter(form_type__in=['F2N']).order_by('-filing_number')[:100]
    title="Newest candidate declaration filings"
    explanatory_text="These are the 100 most recent new electronic statement of candidacy filings received. Note that candidates do not have to file these statements electonically, though many do."
    return newest_filings_template(request, filings, explanatory_text, title)



    
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




    