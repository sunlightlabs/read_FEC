import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import redirect
from django.contrib.localflavor.us.us_states import US_STATES
from django.db.models import Sum

from fec_alerts.models import new_filing, newCommittee
from summary_data.models import Candidate_Overlay, District, Committee_Overlay, Committee_Time_Summary, Authorized_Candidate_Committees, Pac_Candidate
this_cycle = '2014'
this_cycle_start = datetime.date(2013,1,1)
from formdata.models import SkedA, SkedB, SkedE
from summary_data.utils.summary_utils import map_summary_form_to_dict
# get not null senate ids. 
#senate_ids =  [ senator['fec_id'] for senator in senate_crosswalk if senator['fec_id'] ]
from django.conf import settings
from summary_data.utils.update_utils import get_update_time

from django.views.decorators.cache import cache_page

STATE_LIST = [{'name':x[1], 'abbrev':x[0]} for x in US_STATES]



try:
    PAGINATE_BY = settings.REST_FRAMEWORK['PAGINATE_BY']
except:
    print "Missing rest framework default pagination size. Using default."
    PAGINATE_BY = 100

try:
    BULK_EXPORT_KEY  = settings.BULK_EXPORT_KEY
except AttributeError:
    print "Missing bulk dowload key -- please enter a BULK_EXPORT_KEY in settings.py"

try:
    LONG_CACHE_TIME = settings.LONG_CACHE_TIME
    SHORT_CACHE_TIME = settings.SHORT_CACHE_TIME
except AttributeError:
    print "Missing cache times; using defaults"
    LONG_CACHE_TIME = 60
    SHORT_CACHE_TIME = 30


def newbase(request):
    return render_to_response('datapages/realtime_base.html', {}, context_instance=RequestContext(request))
    
def home_page(request):
    # should eventually have a home page, or straighten out urls
    return redirect('/newest-filings/')

"""
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
"""
@cache_page(LONG_CACHE_TIME)
def senate(request):

    title="Senate - Cycle Summary"
    explanatory_text="Fundraising totals are since the beginning of the election cycle (Jan. 1, 2013) for current U.S. senators and Senate candidates who reported having $1,000 or more, or who have been targeted by $1,000 or more in independent expenditures. Only candidates actually running in the current cycle who filed a statement of candidacy are included. If we included anyone who isn't running--or missed anyone who is, please <a href='mailto:realtimefec@sunlightfoundation.com'>let us know</a>. Please note these totals reflect current FEC filings and may not match the summarized data available elsewhere on Influence Explorer."

    # Give up on ORM for data; we're not willing to enforce all the relationships required for them
    districts = District.objects.filter(office='S')

    legislators = Candidate_Overlay.objects.filter(office='S').filter(Q(cash_on_hand__gte=1000)|Q(is_incumbent=True)|Q(total_expenditures__gte=1000)).select_related('district').order_by('-cash_on_hand')

    return render_to_response('datapages/senate_legislator_list.html',
        {
        'STATE_LIST':STATE_LIST,
        'districts':districts,
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        }, 
        context_instance=RequestContext(request)
    )

@cache_page(LONG_CACHE_TIME)
def house(request):

    title="House - Cycle Summary"
    explanatory_text="Fundraising totals are for the entire election cycle for current U.S. House members and House candidates who reported having $1,000 or more, or who have been targeted by $1,000 or more in independent expenditures. Only candidates actually running in the current cycle who filed a statement of candidacy are included. If we included anyone who isn't running--or missed anyone who is, please <a href='mailto:realtimefec@sunlightfoundation.com'>let us know</a>. Please note these totals reflect current FEC filings and may not match the summarized data available elsewhere on Influence Explorer."
    # Give up on ORM for data; we're not willing to enforce all the relationships required for them

    legislators = Candidate_Overlay.objects.filter(office='H').filter(Q(cash_on_hand__gte=1000)|Q(is_incumbent=True)|Q(total_expenditures__gte=1000)).select_related('district').order_by('-cash_on_hand')
    
    districts = District.objects.filter(office='H')

    return render_to_response('datapages/house_legislator_list.html',
        {
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        'STATE_LIST':STATE_LIST,
        'districts':districts,
        }, 
        context_instance=RequestContext(request)
    )

@cache_page(LONG_CACHE_TIME)
def races(request):

    title="Race-wide spending totals"
    explanatory_text="District totals (ie. House and Senate races) are based on the most recent information available, but different political groups report to the FEC on different schedules. Super PACs must report independent expenditures within 48- or 24-hours, but candidate committees only disclose on a quarterly basis. Please note these totals reflect current FEC filings and may not match the summarized data available elsewhere on Influence Explorer."

    districts = District.objects.all()

    return render_to_response('datapages/races.html',
        {
        'STATE_LIST':STATE_LIST,
        'title':title,
        'explanatory_text':explanatory_text,
        'races':districts,
        }, 
        context_instance=RequestContext(request)
    )

# this is a fallback--the IE api doesn't know the senate term classes, so can't create the full race url. It does have the raceid though. The full fix is to make the ie api include the senate term class, but...
def race_id_redirect(request, race_id):
    race = get_object_or_404(District, pk=race_id)
    return redirect(race.get_absolute_url())

@cache_page(LONG_CACHE_TIME)
def house_race(request, cycle, state, district):
    race = get_object_or_404(District, cycle=cycle, state=state, office_district=district, office='H')
    title = race.race_name()
    candidates = Candidate_Overlay.objects.filter(district=race).filter(Q(total_receipts__gte=1000)|Q(total_expenditures__gte=1000)).exclude(not_seeking_reelection=True).order_by('-cash_on_hand')
    outside_spenders = Pac_Candidate.objects.filter(candidate__in=candidates, total_ind_exp__gte=5000).select_related('committee', 'candidate')
    candidate_list = [x.get('fec_id') for x in candidates.values('fec_id')]
    
    recent_ies = SkedE.objects.filter(candidate_id_checked__in=candidate_list, expenditure_amount__gte=1000, superceded_by_amendment=False, expenditure_date_formatted__gte=this_cycle_start).select_related('candidate_checked').order_by('-expenditure_date_formatted')[:5]
    
    committees = Committee_Overlay.objects.filter(curated_candidate__in=candidates)
    committee_ids = [x.get('fec_id') for x in committees.values('fec_id')]
    recent_filings = new_filing.objects.filter(fec_id__in=committee_ids, is_superceded=False).exclude(coverage_to_date__isnull=True).order_by('-coverage_to_date')[:5]
    print recent_filings
    
    return render_to_response('datapages/race_detail.html', 
        {
        'candidates':candidates,
        'title':title,
        'race':race,
        'outside_spenders':outside_spenders,
        'recent_ies':recent_ies,
        'recent_filings':recent_filings,
        },
        context_instance=RequestContext(request)
    )
    
@cache_page(LONG_CACHE_TIME)
def senate_race(request, cycle, state, term_class):
    race = get_object_or_404(District, cycle=cycle, state=state, term_class=term_class, office='S')
    title = race.race_name()
    candidates = Candidate_Overlay.objects.filter(district=race).filter(Q(total_receipts__gte=1000)|Q(total_expenditures__gte=1000)).exclude(not_seeking_reelection=True).order_by('-total_receipts')
    outside_spenders = Pac_Candidate.objects.filter(candidate__in=candidates, total_ind_exp__gte=5000).select_related('committee', 'candidate')
    candidate_list = [x.get('fec_id') for x in candidates.values('fec_id')]
    
    recent_ies = SkedE.objects.filter(candidate_id_checked__in=candidate_list, expenditure_amount__gte=1000, superceded_by_amendment=False, expenditure_date_formatted__gte=this_cycle_start).select_related('candidate_checked').order_by('-expenditure_date_formatted')[:5]
    
    
    return render_to_response('datapages/race_detail.html', 
        {
        'candidates':candidates,
        'title':title,
        'race':race,
        'outside_spenders':outside_spenders,
        'recent_ies':recent_ies,
        },
        context_instance=RequestContext(request)
    )
    
@cache_page(SHORT_CACHE_TIME)
def newest_filings(request):
    candidates = Candidate_Overlay.objects.filter(office='H').order_by('name')
    return render_to_response('datapages/dynamic_filings.html', 
        {
        'candidates':candidates,
        'title':'Newest Filings',
        'PAGINATE_BY':PAGINATE_BY,
        'explanatory_text':'Find and filter the latest electronic campaign finance filings made to the Federal Election Commission. Use the tabs below to filter and sort the type of filings showed. Only House candidates who have raised money are shown in the candidate dropdown menu.  For more details, see the <a href="/about/#newest_filings" class="link">about page</a>.<br><b>Senate candidates do not file electronic reports.</b>',
        },
        context_instance=RequestContext(request)
    )

@cache_page(LONG_CACHE_TIME)
def pacs(request):
    return render_to_response('datapages/dynamic_pacs.html', 
        {
        'explanatory_text':'Find and filter committee summary information for the entire election cycle (since Jan. 1, 2013). Review how much groups raised and spent, their debts and cash on hand. Click the committee name to see filings. For more, see a <a href="/about/#pacs">more detailed explanation</a>.',
        'title':'Political action committee summaries',
        'PAGINATE_BY':PAGINATE_BY,
        },
        context_instance=RequestContext(request)
    ) 

@cache_page(LONG_CACHE_TIME)
def dynamic_ies(request):
    districts = District.objects.filter(outside_spending__gt=1000).order_by('state', 'office', 'office_district')
    candidates = Candidate_Overlay.objects.filter(total_expenditures__gt=1).select_related('district').order_by('name')
    outside_spenders = Committee_Overlay.objects.filter(total_indy_expenditures__gte=1000).order_by('name')
    
    return render_to_response('datapages/dynamic_ies.html', 
        {
        'STATE_LIST':STATE_LIST,
        'title':'Outside Expenditures',
        'explanatory_text':'Find and filter the latest independent expenditures reported. Only races and candidates that have reported independent expenditures of $1,000 or more are given as menu choices. For more, see a <a href="/about/#outside-spending">more detailed explanation</a>.',
        'PAGINATE_BY':PAGINATE_BY,
        'districts':districts,
        'candidates':candidates,
        'outside_spenders':outside_spenders,
        },
        context_instance=RequestContext(request)
    )
    
@cache_page(LONG_CACHE_TIME)
def new_committees(request):
    today = datetime.datetime.today()
    month_ago = today - datetime.timedelta(days=30)
    committees=newCommittee.objects.filter(date_filed__gte=month_ago).order_by('-date_filed')
    return render_to_response('datapages/new_committees.html', {
                'object_list':committees,
                'explanatory_text':'These are political committees formed within the last 30 days. It may take several days after a PAC is formed for details to be posted. Click the arrow on the column headers to sort by date, type or name.',
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
    
    title="Bulk Downloads" 
    update_time = get_update_time(BULK_EXPORT_KEY)

    return render_to_response('datapages/downloads.html',
        {
        'title':title,
        'update_time':update_time,
        }, 
        context_instance=RequestContext(request)
    )

def about(request):

    title="About Realtime Federal Campaign Finance" 

    return render_to_response('datapages/about.html',
        {
        'title':title,
        }, 
        context_instance=RequestContext(request)
    )

@cache_page(LONG_CACHE_TIME)
def outside_spending(request):
    
    
    title="Independent Expenditures" 
    explanatory_text = "Only independent expenditures of $10,000 or more are shown"


    ies = SkedE.objects.filter(superceded_by_amendment=False, expenditure_amount__gte=10000, expenditure_date_formatted__gte=datetime.date(2013,1,1)).select_related('candidate_checked', 'district_checked').order_by('-expenditure_date_formatted')

    return render_to_response('datapages/outside_spending.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'object_list':ies,
        }, 
        context_instance=RequestContext(request)
    )

@cache_page(LONG_CACHE_TIME)
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

@cache_page(LONG_CACHE_TIME)
def filings_skeda(request, filing_num):
    filing_data = get_object_or_404(new_filing, filing_number=filing_num)
    title="Itemized Receipts, <a href=\"%s\">%s</a> filing #<a href=\"%s\">%s</a>" % (filing_data.get_committee_url(), filing_data.committee_name, filing_data.get_absolute_url(), filing_num)
    
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
@cache_page(LONG_CACHE_TIME)
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
@cache_page(LONG_CACHE_TIME)
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

@cache_page(LONG_CACHE_TIME)
def committee(request, committee_id):
    committee_overlay = get_object_or_404(Committee_Overlay, fec_id=committee_id)
        
    title = committee_overlay.name
    report_list = Committee_Time_Summary.objects.filter(com_id=committee_id, coverage_from_date__gte=this_cycle_start).order_by('-coverage_through_date')
    
    
    end_of_coverage_date = committee_overlay.cash_on_hand_date
    recent_report_list = None
    
    if end_of_coverage_date:
        recent_report_list = new_filing.objects.filter(fec_id=committee_id, coverage_from_date__gte=end_of_coverage_date, form_type__in=['F5A', 'F5', 'F5N', 'F24', 'F24A', 'F24N', 'F6', 'F6A', 'F6N']).exclude(is_f5_quarterly=True).exclude(is_superceded=True)
    else:
        recent_report_list = new_filing.objects.filter(fec_id=committee_id, coverage_from_date__gte=this_cycle_start, form_type__in=['F5A', 'F5', 'F5N', 'F24', 'F24A', 'F24N', 'F6', 'F6A', 'F6N']).exclude(is_f5_quarterly=True).exclude(is_superceded=True)
        
    independent_spending = Pac_Candidate.objects.filter(committee=committee_overlay, total_ind_exp__gte=5000).select_related('candidate')
    
    recent_ies = None
    if committee_overlay.total_indy_expenditures > 5000:
        recent_ies = SkedE.objects.filter(filer_committee_id_number=committee_id, expenditure_amount__gte=5000, superceded_by_amendment=False, expenditure_date_formatted__gte=this_cycle_start).select_related('candidate_checked').order_by('-expenditure_date_formatted')[:10]
        
    
    return render_to_response('datapages/committee.html',
        {
        'title':title,
        'report_list':report_list,
        'recent_report_list':recent_report_list,
        'committee':committee_overlay,
        'independent_spending':independent_spending,
        'recent_ies':recent_ies,
        }, 
        context_instance=RequestContext(request)
    )
    
@cache_page(LONG_CACHE_TIME)
def candidate(request, candidate_id):
    candidate_overlay = get_object_or_404(Candidate_Overlay, fec_id=candidate_id)
    title = "%s (%s) " % (candidate_overlay.name, candidate_overlay.party)
    
    authorized_committee_list = Authorized_Candidate_Committees.objects.filter(candidate_id=candidate_id)
    committee_list = [x.get('committee_id') for x in authorized_committee_list.values('committee_id')]
    
    report_list = Committee_Time_Summary.objects.filter(com_id__in=committee_list, coverage_from_date__gte=this_cycle_start).order_by('-coverage_through_date')
    
    
    end_of_coverage_date = None
    recent_report_list = None
    if report_list:
        end_of_coverage_date = report_list[0].coverage_through_date
        
    
    recent_report_total = 0
    if end_of_coverage_date:
        recent_report_list = new_filing.objects.filter(fec_id__in=committee_list, coverage_from_date__gte=end_of_coverage_date, form_type__in=['F6', 'F6A', 'F6N']).exclude(is_superceded=True)
        if recent_report_list:
            recent_report_total = recent_report_list.aggregate(spending_total=Sum('tot_raised'))['spending_total']
        
    else:
        recent_report_list = new_filing.objects.filter(fec_id__in=committee_list, coverage_from_date__gte=this_cycle_start, form_type__in=['F6', 'F6A', 'F6N']).exclude(is_superceded=True)
    
    
    # are their outside groups who've spent for/against this candidate? 
    outside_spenders = Pac_Candidate.objects.filter(candidate=candidate_overlay, total_ind_exp__gte=1000).select_related('committee')
    
    recent_ies = None
    if outside_spenders:
        recent_ies = SkedE.objects.filter(candidate_checked=candidate_overlay, expenditure_amount__gte=5000, superceded_by_amendment=False, expenditure_date_formatted__gte=this_cycle_start).select_related('candidate_checked').order_by('-expenditure_date_formatted')[:10]
    
    
    return render_to_response('datapages/candidate.html',
        {
        'title':title,
        'report_list':report_list,
        'candidate':candidate_overlay,
        'authorized_committee_list':authorized_committee_list,
        'outside_spenders':outside_spenders,
        'recent_report_list':recent_report_list,
        'recent_ies':recent_ies,
        'recent_report_total':recent_report_total,
        }, 
        context_instance=RequestContext(request)
    )
@cache_page(LONG_CACHE_TIME)
def subscribe(request):
    return render_to_response('datapages/subscribe.html',
        {
        'title':'Subscribe to alerts',
        }, 
        context_instance=RequestContext(request)
    )
@cache_page(LONG_CACHE_TIME)
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




    