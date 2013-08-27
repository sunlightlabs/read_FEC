import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import redirect


from fec_alerts.models import new_filing, newCommittee
from summary_data.models import Candidate_Overlay, District, Committee_Overlay, Committee_Time_Summary, Authorized_Candidate_Committees
this_cycle = '2014'
this_cycle_start = datetime.date(2013,1,1)
from formdata.models import SkedA, SkedB, SkedE
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
    
def home_page(request):
    # should eventually have a home page, or straighten out urls
    return redirect('/newest-filings/')


def candidates(request):

    title="Candidates - Cycle Summary"
    explanatory_text="This page shows the fundraising totals for the entire cycle for current candidates."
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

    title="Senate - Cycle Summary"
    explanatory_text="Fundraising totals are from 1/1/13 through the present for current senators and senate candidates who reported having $1,000 or more. "

    # Give up on ORM for data; we're not willing to enforce all the relationships required for them

    legislators = Candidate_Overlay.objects.filter(office='S', cash_on_hand__gte=1000)

    return render_to_response('datapages/legislator_list.html',
        {
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        }, 
        context_instance=RequestContext(request)
    )

def house(request):

    title="House - Cycle Summary"
    explanatory_text="Fundraising totals are for the entire cycle for current house members and house candidates who reported having $1,000 or more. "
    # Give up on ORM for data; we're not willing to enforce all the relationships required for them

    legislators = Candidate_Overlay.objects.filter(office='H', cash_on_hand__gte=1000)

    return render_to_response('datapages/legislator_list.html',
        {
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        }, 
        context_instance=RequestContext(request)
    )


def races(request):

    title="Race-wide spending totals"
    explanatory_text="District totals are based on the most recent information available, but different political groups report this on different schedules. Super PACs must reported independent expenditures within 48- or 24-hours, but candidate committees only report this quarterly."

    districts = District.objects.all()

    return render_to_response('datapages/races.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'races':districts,
        }, 
        context_instance=RequestContext(request)
    )



def house_race(request, cycle, state, district):
    race = get_object_or_404(District, cycle=cycle, state=state, office_district=district, office='H')
    title = race.race_name()
    candidates = Candidate_Overlay.objects.filter(district=race)
    return render_to_response('datapages/race_detail.html', 
        {
        'candidates':candidates,
        'title':title,
        'race':race,
        },
        context_instance=RequestContext(request)
    )
    
    
def senate_race(request, cycle, state, term_class):
    race = get_object_or_404(District, cycle=cycle, state=state, term_class=term_class, office='S')
    title = race.race_name()
    candidates = Candidate_Overlay.objects.filter(district=race)
    return render_to_response('datapages/race_detail.html', 
        {
        'candidates':candidates,
        'title':title,
        'race':race,
        },
        context_instance=RequestContext(request)
    )

def newest_filings(request):
    return render_to_response('datapages/dynamic_filings.html', 
        {
        'title':'Newest Filings',
        'PAGINATE_BY':PAGINATE_BY,
        },
        context_instance=RequestContext(request)
    )
     
def pacs(request):
    return render_to_response('datapages/dynamic_pacs.html', 
        {
        'title':'PAC summaries',
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


def outside_spending(request):
    return render_blank_page('Outside Spending','This is a page on outside spending. Maybe include links to subpages on electioneering, and coordinated spending? I dunno.', request)

def filing(request, filing_num):
    filing = get_object_or_404(new_filing, filing_number=filing_num)
    committee = None
    title="%s:details of filing #%s" % ( filing.committee_name, filing_num)
    
    try:
        committee = Committee_Overlay.objects.get(fec_id = filing.fec_id)
        title="<a href=\"%s\">%s</a>: details of filing #%s" % (committee.get_absolute_url(), filing.committee_name, filing_num)
        
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
    
    
    end_of_coverage_date = committee_overlay.cash_on_hand_date
    recent_report_list = None
    
    if end_of_coverage_date:
        recent_report_list = new_filing.objects.filter(fec_id=committee_id, coverage_from_date__gte=end_of_coverage_date, form_type__in=['F5A', 'F5', 'F5N', 'F24', 'F24A', 'F24N', 'F6', 'F6A', 'F6N']).exclude(is_f5_quarterly=True).exclude(is_superceded=True)
    else:
        recent_report_list = new_filing.objects.filter(fec_id=committee_id, coverage_from_date__gte=this_cycle_start, form_type__in=['F5A', 'F5', 'F5N', 'F24', 'F24A', 'F24N', 'F6', 'F6A', 'F6N']).exclude(is_f5_quarterly=True).exclude(is_superceded=True)
        
    
    return render_to_response('datapages/committee.html',
        {
        'title':title,
        'report_list':report_list,
        'recent_report_list':recent_report_list,
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
        'title':'Subscribe to alerts',
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




    