import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection

from fec_alerts.models import new_filing, newCommittee
from summary_data.models import Candidate_Overlay, District
this_cycle = '2014'
# get not null senate ids. 
#senate_ids =  [ senator['fec_id'] for senator in senate_crosswalk if senator['fec_id'] ]

def house(request):

    title="House Members - Cycle Summary"
    explanatory_text="This page shows the fundraising totals for the entire cycle for current house members. For cyclewide totals for challengers, see the <a href=\"/candidates/\">candidates</a> page. For fundraising totals for just a single reporting period, see the <a href=\"/reports\">reports</a> page."
    # Give up on ORM for data; we're not willing to enforce all the relationships required for them
    
    legislators = Candidate_Overlay.objects.filter(cycle=this_cycle, office='H', cand_ici='I')
    
    return render_to_response('datapages/legislator_list.html',
        {
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        }
    )
    
def senate(request):

    title="Senators - Cycle Summary"
    explanatory_text="This page shows the fundraising totals for the entire cycle for current senators. For cyclewide totals for challengers, see the <a href=\"/candidates/\">candidates</a> page. For fundraising totals for just a single reporting period, see the <a href=\"/reports\">reports</a> page."

    # Give up on ORM for data; we're not willing to enforce all the relationships required for them

    legislators = Candidate_Overlay.objects.filter(cycle=this_cycle, office='S', cand_ici='I')

    return render_to_response('datapages/legislator_list.html',
        {
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        }
    )

def districts(request):

    title="District Spending Comparison"
    explanatory_text="District totals are based on the most recent information available, but different political groups report this differently. Super PACs must reported independent expenditures within 48- or 24-hours, but candidate committees typically report this quarterly."

    # Give up on ORM for data; we're not willing to enforce all the relationships required for them

    senate_districts = District.objects.filter(office='S').order_by('state')
    house_districts = District.objects.filter(office='H').order_by('state', 'office_district')

    return render_to_response('datapages/districts.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'senate_districts':senate_districts,
        'house_districts':house_districts,
        }
    )

def newest_filings_template(request, filings, explanatory_text, title):
        explanatory_text = explanatory_text + "<br>See also:&nbsp; <a href=\"/newest-filings/ies/\">independent expenditure filings</a>&nbsp;|&nbsp;<a href=\"/newest-filings/candidacy/\">declarations of candidacy</a>&nbsp;|&nbsp;<a href=\"/newest-filings/candidate-filings/\">new candidate committee reports</a>&nbsp;|&nbsp;<a href=\"/newest-filings/\">all new filings</a>"
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

def newest_filings_candidacy(request):
    filings = new_filing.objects.filter(form_type__in=['F2N']).order_by('-filing_number')[:100]
    title="Newest candidate declaration filings"
    explanatory_text="These are the 100 most recent new electronic statement of candidacy filings received. Note that candidates do not have to file these statements electonically, though many do."
    return newest_filings_template(request, filings, explanatory_text, title)

def newest_filings_candidate_filings(request):
    filings = new_filing.objects.filter(form_type__in=['F3N']).order_by('-filing_number')[:100]
    title="Newest candidate declaration filings"
    explanatory_text="These are the 100 most recent new electronic statements from authorized commit."
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

### Placeholder pages

def render_blank_page(title, explanatory_text):
    return render_to_response('datapages/blank_page.html', {
        'title':title,
        'explanatory_text':explanatory_text,
                })
                
def downloads(request):
    return render_blank_page('Downloads','Downloadable files will go here.')

def pacs(request):
    return render_blank_page('PACs','This page is a searchable, sortable, filterable paginated list of all pacs and their cycle-to-date fundraising numbers. Filters are for things like super-pacs, candidate pacs, leadership pacs (maybe), and maybe a category for NRCC/DSCC etc.')

def candidates(request):
    return render_blank_page('Candidates','This page is a searchable, sortable, filterable paginated list of all pacs and their cycle-to-date fundraising numbers. Filter by race or by chamber, I think.')

def reports(request):
    return render_blank_page('Reports','This page is a searchable, sortable, filterable paginated list of summary reports for pacs. Instead of showing cycle-to-date numbers, like on most other pages, this one will show just the fundraising totals for a single filing period.')        

def alerts(request):
    return render_blank_page('Alerts','This is where you sign up to receive alerts. This time we should make alerts for a specific race too. New filing alerts should include summary details--so the amount raised in the newly-filed filing.')

def outside_spending(request):
    return render_blank_page('Outside Spending','This is a page on outside spending. Maybe include links to subpages on electioneering, and coordinated spending? I dunno.')