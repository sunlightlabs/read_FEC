import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection
from django.db.models import Q
from django.template import RequestContext


from fec_alerts.models import new_filing, newCommittee
from summary_data.models import Candidate_Overlay, District, Committee_Overlay, Committee_Time_Summary, Authorized_Candidate_Committees
this_cycle = '2014'
this_cycle_start = datetime.date(2013,1,1)
from formdata.models import Filing_Header, SkedA, SkedB, SkedE
from summary_data.utils.summary_utils import map_summary_form_to_dict
# get not null senate ids. 
#senate_ids =  [ senator['fec_id'] for senator in senate_crosswalk if senator['fec_id'] ]
from django.conf import settings

try:
    PAGINATE_BY = settings.REST_FRAMEWORK['PAGINATE_BY']
except KeyError:
    print "Missing rest framework default pagination size. "
    PAGINATE_BY = 100

def newbase(request):
    return render_to_response('datapages/realtime_base.html', {}, context_instance=RequestContext(request))
    
def house(request):

    title="House Members - Cycle Summary"
    explanatory_text="This page shows the fundraising totals for the entire cycle for current house members. For cyclewide totals for challengers, see the <a href=\"/candidates/\">candidates</a> page. For fundraising totals for just a single reporting period, see the <a href=\"/reports\">reports</a> page."
    # Give up on ORM for data; we're not willing to enforce all the relationships required for them
    
    legislators = Candidate_Overlay.objects.filter(office='H', is_incumbent=True)
    
    return render_to_response('datapages/legislator_list.html',
        {
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        }, 
        context_instance=RequestContext(request)
    )
    

def candidates(request):

    title="Candidates - Cycle Summary"
    explanatory_text="This page shows the fundraising totals for the entire cycle for current candidates. For fundraising totals for just a single reporting period, see the <a href=\"/reports\">reports</a> page."
    # Give up on ORM for data; we're not willing to enforce all the relationships required for them

    legislators = Candidate_Overlay.objects.all()

    return render_to_response('datapages/candidate_list.html',
        {
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        }, 
        context_instance=RequestContext(request)
    )
def senate(request):

    title="Senators - Cycle Summary"
    explanatory_text="This page shows the fundraising totals for the entire cycle for current senators. For cyclewide totals for challengers, see the <a href=\"/candidates/\">candidates</a> page. For fundraising totals for just a single reporting period, see the <a href=\"/reports\">reports</a> page."

    # Give up on ORM for data; we're not willing to enforce all the relationships required for them

    legislators = Candidate_Overlay.objects.filter(office='S', is_incumbent=True)

    return render_to_response('datapages/legislator_list.html',
        {
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        }, 
        context_instance=RequestContext(request)
    )

def races(request):

    title="Race Spending Comparison"
    explanatory_text="District totals are based on the most recent information available, but different political groups report this differently. Super PACs must reported independent expenditures within 48- or 24-hours, but candidate committees typically report this quarterly."

    senate_districts = District.objects.filter(office='S').order_by('state')
    house_districts = District.objects.filter(office='H').order_by('state', 'office_district')

    return render_to_response('datapages/districts.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'senate_districts':senate_districts,
        'house_districts':house_districts,
        }, 
        context_instance=RequestContext(request)
    )

def newest_filings(request):
    return render_to_response('datapages/dynamic_filings.html', 
        {
        'PAGINATE_BY':PAGINATE_BY,
        },
        context_instance=RequestContext(request)
    )
     
def pacs(request):
    return render_to_response('datapages/dynamic_pacs.html', 
        {
        'PAGINATE_BY':PAGINATE_BY,
        },
        context_instance=RequestContext(request)
    )  
def new_committees(request):
    today = datetime.datetime.today()
    month_ago = today - datetime.timedelta(days=30)
    committees=newCommittee.objects.filter(date_filed__gte=month_ago).order_by('-date_filed')
    return render_to_response('datapages/new_committees.html', {
                'object_list':committees,
                'explanatory_text':'These are committees formed within the last 30 days. It may take several days after a PAC is formed for details to be posted.',
                'title':'New Committees'
                }, 
                context_instance=RequestContext(request)
                )

### Placeholder pages

def render_blank_page(title, explanatory_text, request):
    return render_to_response('datapages/blank_page.html', {
        'title':title,
        'explanatory_text':explanatory_text,
                }, 
                context_instance=RequestContext(request)
                )
                
def downloads(request):
    return render_blank_page('Downloads','Downloadable files will go here.', request)


def alerts(request):
    return render_blank_page('Alerts','This is where you sign up to receive alerts. This time we should make alerts for a specific race too. New filing alerts should include summary details--so the amount raised in the newly-filed filing.', request)

def outside_spending(request):
    return render_blank_page('Outside Spending','This is a page on outside spending. Maybe include links to subpages on electioneering, and coordinated spending? I dunno.', request)

def filing(request, filing_num):
    filing = get_object_or_404(new_filing, filing_number=filing_num)
    committee = None
    title="%s:details of filing #%s" % ( filing.committee_name, filing_num)
    
    try:
        committee = Committee_Overlay.objects.get(fec_id = filing.fec_id)
        title="<a href=\"%s\">%s</a>:details of filing #%s" % (committee.get_absolute_url(), filing.committee_name, filing_num)
        
    except:
        pass
    
    return render_to_response('datapages/filing.html',
        {
        'title':title,
        'filing':filing,
        'committee':committee,
        }, 
        context_instance=RequestContext(request)
    )
    
def filings_skeda(request, filing_num):
    filing_data = get_object_or_404(new_filing, filing_number=filing_num)
    title="Contributions, <a href=\"%s\">%s</a> filing #<a href=\"%s\">%s</a>" % (filing_data.get_committee_url(), filing_data.committee_name, filing_data.get_absolute_url(), filing_num)
    
    filings = None
    too_many_to_display = False
    if filing_data.lines_present:
        lines_present = filing_data.lines_present.get('A')
        if int(lines_present) <= 1000:
            filings = SkedA.objects.filter(filing_number=filing_num).order_by('-contribution_amount')
        else:
            too_many_to_display = True
    
    return render_to_response('datapages/filing_skeda.html',
        {
        'title':title,
        'object_list':filings,
        'too_many_to_display':too_many_to_display,
        'filing_data':filing_data,
        }, 
        context_instance=RequestContext(request)
    )

def filings_skedb(request, filing_num):
    filing_data = get_object_or_404(new_filing, filing_number=filing_num)
    title="Disbursements, <a href=\"%s\">%s</a> filing #<a href=\"%s\">%s</a>" % (filing_data.get_committee_url(), filing_data.committee_name, filing_data.get_absolute_url(), filing_num)

    filings = None
    too_many_to_display = False
    if filing_data.lines_present:
        lines_present = filing_data.lines_present.get('B')
        if int(lines_present) <= 1000:
            filings = SkedB.objects.filter(filing_number=filing_num).order_by('-expenditure_amount')
        else:
            too_many_to_display = True

    return render_to_response('datapages/filing_skedb.html',
        {
        'title':title,
        'object_list':filings,
        'too_many_to_display':too_many_to_display,
        'filing_data':filing_data,
        }, 
        context_instance=RequestContext(request)
    )

def filings_skede(request, filing_num):
    filing_data = get_object_or_404(new_filing, filing_number=filing_num)
    title="Independent Expenditures, <a href=\"%s\">%s</a> filing #<a href=\"%s\">%s</a>" % (filing_data.get_committee_url(), filing_data.committee_name, filing_data.get_absolute_url(), filing_num)

    filings = None
    too_many_to_display = False
    if filing_data.lines_present:
        lines_present = filing_data.lines_present.get('E')
        if int(lines_present) <= 1000:
            filings = SkedE.objects.filter(filing_number=filing_num).order_by('-expenditure_amount')
        else:
            too_many_to_display = True

    return render_to_response('datapages/filing_skede.html',
        {
        'title':title,
        'object_list':filings,
        'too_many_to_display':too_many_to_display,
        'filing_data':filing_data,
        }, 
        context_instance=RequestContext(request)
    )


def committee(request, committee_id):
    committee_overlay = get_object_or_404(Committee_Overlay, fec_id=committee_id)
        
    title = committee_overlay.name
    report_list = Committee_Time_Summary.objects.filter(com_id=committee_id, coverage_from_date__gte=this_cycle_start).order_by('coverage_through_date')
    return render_to_response('datapages/committee.html',
        {
        'title':title,
        'report_list':report_list,
        'committee':committee_overlay,
        }, 
        context_instance=RequestContext(request)
    )
    

def candidate(request, candidate_id):
    candidate_overlay = get_object_or_404(Candidate_Overlay, fec_id=candidate_id)
    title = "%s (%s) " % (candidate_overlay.name, candidate_overlay.party)
    
    authorized_committee_list = Authorized_Candidate_Committees.objects.filter(candidate_id=candidate_id)
    committee_list = [x.get('committee_id') for x in authorized_committee_list.values('committee_id')]
    
    report_list = Committee_Time_Summary.objects.filter(com_id__in=committee_list, coverage_from_date__gte=this_cycle_start).order_by('coverage_through_date')
    return render_to_response('datapages/candidate.html',
        {
        'title':title,
        'report_list':report_list,
        'candidate':candidate_overlay,
        'authorized_committee_list':authorized_committee_list,
        }, 
        context_instance=RequestContext(request)
    )

def subscribe(request):
    return render_to_response('datapages/subscribe.html',
        {
        }, 
        context_instance=RequestContext(request)
    )

def committee_search_html(request): 
    params = request.GET
    committees = None

    try:
        committee_name_fragment =  params['name']
        if len(committee_name_fragment) > 3:
            print committee_name_fragment


            committees = Committee_Overlay.objects.filter(Q(name__icontains=committee_name_fragment) | Q(curated_candidate__name__icontains=committee_name_fragment)).select_related('curated_candidate')
        else:
            committees = None
    except KeyError:
        committees = None

    return render_to_response('datapages/committee_search.html',
        {
        'committees':committees,
        }
    )




    