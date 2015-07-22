import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import redirect
from django.contrib.localflavor.us.us_states import US_STATES
from django.db.models import Sum
from django.http import Http404

from fec_alerts.models import new_filing, newCommittee, f1filer
from summary_data.models import Candidate_Overlay, District, Committee_Overlay, Committee_Time_Summary, Authorized_Candidate_Committees, Pac_Candidate, DistrictWeekly
from shared_utils.cycle_utils import get_cycle_abbreviation, is_valid_four_digit_string_cycle, get_cycle_endpoints, list_2014_only, list_2016_only, cycle_fake

this_cycle = '2014'
this_cycle_start = datetime.date(2013,1,1)
from formdata.models import SkedA, SkedB, SkedE
from summary_data.utils.summary_utils import map_summary_form_to_dict
# get not null senate ids. 
#senate_ids =  [ senator['fec_id'] for senator in senate_crosswalk if senator['fec_id'] ]
from django.conf import settings
from summary_data.utils.update_utils import get_update_time
from summary_data.utils.weekly_update_utils import get_week_number, get_week_start, get_week_end
from summary_data.election_dates import elections_by_day
from summary_data.management.commands.write_weekly_files import data_series as weekly_dump_data_series
from summary_data.utils.chart_reference import chart_name_reference, chart_donor_name_reference

from django.views.decorators.cache import cache_page, cache_control

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

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'




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
def senate(request, cycle):
    
    if not is_valid_four_digit_string_cycle(cycle):
        # should redirect, but for now:
        raise Http404
        
    title="Senate - Cycle Summary"
    explanatory_text="Fundraising totals are for the selected two-year election cycle for Senate candidates who reported having $1,000 or more, or who have been targeted by $1,000 or more in independent expenditures. Only candidates actually running in the current cycle who filed a statement of candidacy are included. If we included anyone who isn't running--or missed anyone who is, please <a href='mailto:realtimefec@sunlightfoundation.com'>let us know</a>. Please note these totals reflect current FEC filings and may not match the summarized data available elsewhere on Influence Explorer."

    # Give up on ORM for data; we're not willing to enforce all the relationships required for them
    districts = District.objects.filter(office='S', cycle=cycle)

    legislators = Candidate_Overlay.objects.filter(office='S', cycle=cycle).filter(Q(cash_on_hand__gte=1000)|Q(is_incumbent=True)|Q(total_expenditures__gte=1000)).select_related('district').order_by('-cash_on_hand')
    
    districts = District.objects.filter(office='H', cycle=cycle)

    other_year = None
    if cycle == '2016':
        other_year = '2014'
    elif cycle == '2014':
        other_year = '2016'
    cycle_list = [cycle_fake(cycle, "/senate/%s/" % cycle), cycle_fake(other_year, "/senate/%s/" % other_year)]
    

    return render_to_response('datapages/senate_legislator_list.html',
        {
        'STATE_LIST':STATE_LIST,
        'districts':districts,
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        'cycle_list':cycle_list
        }, 
        context_instance=RequestContext(request)
    )

def senate_redirect(request):
    return redirect("/senate/2016/")

@cache_page(LONG_CACHE_TIME)
def house(request, cycle):

    if not is_valid_four_digit_string_cycle(cycle):
        # should redirect, but for now:
        raise Http404
        
    title="House - Cycle Summary"
    explanatory_text="Fundraising totals are for the selected two-year election cycle for current candidates for U.S. House who reported having $1,000 or more, or who have been targeted by $1,000 or more in independent expenditures. Only candidates actually running in the current cycle who filed a statement of candidacy are included. If we included anyone who isn't running--or missed anyone who is, please <a href='mailto:realtimefec@sunlightfoundation.com'>let us know</a>. Please note these totals reflect current FEC filings and may not match the summarized data available elsewhere on Influence Explorer."
    # Give up on ORM for data; we're not willing to enforce all the relationships required for them

    legislators = Candidate_Overlay.objects.filter(office='H', cycle=cycle).filter(Q(cash_on_hand__gte=1000)|Q(is_incumbent=True)|Q(total_expenditures__gte=1000)).select_related('district').order_by('-cash_on_hand')
    
    
    
    districts = District.objects.filter(office='H', cycle=cycle)

    other_year = None
    if cycle == '2016':
        other_year = '2014'
    elif cycle == '2014':
        other_year = '2016'
    cycle_list = [cycle_fake(cycle, "/house/%s/" % cycle), cycle_fake(other_year, "/house/%s/" % other_year)]


    return render_to_response('datapages/house_legislator_list.html',
        {
        'object_list':legislators,
        'title':title,
        'explanatory_text':explanatory_text,
        'STATE_LIST':STATE_LIST,
        'districts':districts,
        'cycle_list':cycle_list        
        
        }, 
        context_instance=RequestContext(request)
    )

def house_redirect(request):
    return redirect("/house/2016/")

@cache_page(LONG_CACHE_TIME)
def races(request, cycle):
    if not is_valid_four_digit_string_cycle(cycle):
        # should redirect, but for now:
        raise Http404
        
    title="Race-wide spending totals for %s cycle" % (cycle)
    explanatory_text="District totals (ie. House and Senate races) are based on the most recent information available, but different political groups report to the FEC on different schedules. Super PACs must report independent expenditures within 48- or 24-hours, but candidate committees only disclose on a quarterly basis. Please note these totals reflect current FEC filings and may not match the summarized data available elsewhere on Influence Explorer. <br>For primary contests see our list of <a href='/competitive-primaries/'>competitive primaries</a>."


    other_year = None
    if cycle == '2016':
        other_year = '2014'
    elif cycle == '2014':
        other_year = '2016'
    cycle_list = [cycle_fake(cycle, "/races/%s/" % cycle), cycle_fake(other_year, "/races/%s/" % other_year)]

    districts = District.objects.filter(cycle=cycle)

    return render_to_response('datapages/races.html',
        {
        'STATE_LIST':STATE_LIST,
        'title':title,
        'explanatory_text':explanatory_text,
        'races':districts,
        'cycle_list':cycle_list        
        }, 
        context_instance=RequestContext(request)
    )

# old links here will get sent to the new cycle. 
def races_redirect(request):
    return redirect("/races/2016/")
        
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
    
    
    cycle_endpoints = get_cycle_endpoints(int(cycle))
    recent_ies = SkedE.objects.filter(candidate_id_checked__in=candidate_list, expenditure_amount__gte=1000, superceded_by_amendment=False, expenditure_date_formatted__gte=cycle_endpoints['start'], expenditure_date_formatted__lte=cycle_endpoints['end'] ).select_related('candidate_checked').order_by('-expenditure_date_formatted')[:5]
    
    committees = Committee_Overlay.objects.filter(curated_candidate__in=candidates)
    committee_ids = [x.get('fec_id') for x in committees.values('fec_id')]
    recent_filings = new_filing.objects.filter(fec_id__in=committee_ids, is_superceded=False).exclude(coverage_to_date__isnull=True).order_by('-coverage_to_date')[:5]
    
    
    # figure out which cycles are available. The current one goes first, because it is being displayed.     
    cycle_values = District.objects.filter(state=state, office_district=district, office='H').exclude(cycle=cycle)
    cycle_list = [race] + list(cycle_values)
    
    
    return render_to_response('datapages/race_detail.html', 
        {
        'candidates':candidates,
        'title':title,
        'race':race,
        'outside_spenders':outside_spenders,
        'recent_ies':recent_ies,
        'recent_filings':recent_filings,
        'cycle_list':cycle_list
        },
        context_instance=RequestContext(request)
    )



@cache_page(LONG_CACHE_TIME)
def presidential_race(request):
    
    race = get_object_or_404(District, cycle=CURRENT_CYCLE, office='P')
    title = "2016 Presidential Candidates"
    candidates = Candidate_Overlay.objects.filter(district=race).filter(Q(total_receipts__gte=100000)|Q(total_expenditures__gte=100000)).exclude(not_seeking_reelection=True).order_by('-cash_on_hand')
    outside_spenders = Pac_Candidate.objects.filter(candidate__in=candidates, total_ind_exp__gte=100000).select_related('committee', 'candidate')
    candidate_list = [x.get('fec_id') for x in candidates.values('fec_id')]


    cycle_endpoints = get_cycle_endpoints(int(CURRENT_CYCLE))
    recent_ies = SkedE.objects.filter(candidate_id_checked__in=candidate_list, expenditure_amount__gte=10000, superceded_by_amendment=False, expenditure_date_formatted__gte=cycle_endpoints['start'], expenditure_date_formatted__lte=cycle_endpoints['end']).select_related('candidate_checked').order_by('-expenditure_date_formatted')[:5]

    committees = Committee_Overlay.objects.filter(curated_candidate__in=candidates)
    committee_ids = [x.get('fec_id') for x in committees.values('fec_id')]
    recent_filings = new_filing.objects.filter(fec_id__in=committee_ids, is_superceded=False).exclude(coverage_to_date__isnull=True).order_by('-coverage_to_date')[:5]


    # figure out which cycles are available. The current one goes first, because it is being displayed.     
    cycle_list = list_2016_only


    return render_to_response('datapages/presidential_race_detail.html', 
        {
        'candidates':candidates,
        'title':title,
        'race':race,
        'outside_spenders':outside_spenders,
        'recent_ies':recent_ies,
        'recent_filings':recent_filings,
        'cycle_list':cycle_list
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
    
    
    cycle_endpoints = get_cycle_endpoints(int(cycle))    
    recent_ies = SkedE.objects.filter(candidate_id_checked__in=candidate_list, expenditure_amount__gte=1000, superceded_by_amendment=False, expenditure_date_formatted__gte=cycle_endpoints['start'], expenditure_date_formatted__lte=cycle_endpoints['end'] ).select_related('candidate_checked').order_by('-expenditure_date_formatted')[:5]
    
    # figure out which cycles are available. The current one goes first, because it is being displayed.     
    cycle_values = District.objects.filter(state=state, term_class=term_class, office='S').exclude(cycle=cycle)
    cycle_list = [race] + list(cycle_values)
        
    return render_to_response('datapages/race_detail.html', 
        {
        'candidates':candidates,
        'title':title,
        'race':race,
        'outside_spenders':outside_spenders,
        'recent_ies':recent_ies,
        'cycle_list':cycle_list
        },
        context_instance=RequestContext(request)
    )
    
@cache_control(no_cache=True)
def newest_filings(request):
    candidates = Candidate_Overlay.objects.filter(office__in=['H', 'P'], cycle=CURRENT_CYCLE).order_by('name')
    return render_to_response('datapages/dynamic_filings.html', 
        {
        'candidates':candidates,
        'title':'Newest Filings',
        'PAGINATE_BY':PAGINATE_BY,
        'explanatory_text':'Find and filter electronic campaign finance filings made to the Federal Election Commission in the 2013/14 and 2015/16 cycles. Use the tabs below to filter and sort the type of filings showed. Only House candidates who have raised money are shown in the candidate dropdown menu.  For more details, see the <a href="/about/#newest_filings" class="link">about page</a>.<br><b>Senate candidates do not file electronic reports.</b>',
        },
        context_instance=RequestContext(request)
    )

@cache_control(no_cache=True)
def pacs(request, cycle):
    
    if not is_valid_four_digit_string_cycle(cycle):
        raise Http404
        
    other_year = None
    if cycle == '2016':
        other_year = '2014'
    elif cycle == '2014':
        other_year = '2016'
    cycle_list = [cycle_fake(cycle, "/pacs/%s/" % cycle), cycle_fake(other_year, "/pacs/%s/" % other_year)]
    
    return render_to_response('datapages/dynamic_pacs.html', 
        {
        'explanatory_text':'Find and filter committee summary information for an entire two-year cycle (2016 or 2014). Review how much groups raised and spent, their debts and cash on hand. Click the committee name to see filings. For more, see a <a href="/about/#pacs">more detailed explanation</a>.',
        'title':'Political action committee summaries',
        'PAGINATE_BY':PAGINATE_BY,
        'cycle_list':cycle_list
        },
        context_instance=RequestContext(request)
    ) 

# old links here will get sent to the new cycle. 
def pacs_redirect(request):
    return redirect("/pacs/2016/")


@cache_control(no_cache=True)
def outside_spenders(request, cycle):
    
    other_year = None
    if cycle == '2016':
        other_year = '2014'
    elif cycle == '2014':
        other_year = '2016'
    cycle_list = [cycle_fake(cycle, "/outside-spenders/%s/" % cycle), cycle_fake(other_year, "/outside-spenders/%s/" % other_year)]
    
    explanatory_text = "Find and filter outside spender information for the entire %s election cycle. Click the committee name to see filings; click the expenditure amount to see this spending broken down line-by-line. By \"major activity\" we mean the activity the PAC has reported spending the most money on." % cycle
    
    return render_to_response('datapages/dynamic_outside_spenders.html', 
        {
        'explanatory_text':explanatory_text,
        'title':"Outside spending committee summaries (%s cycle)" % cycle,
        'PAGINATE_BY':PAGINATE_BY,
        'cycle_list':cycle_list,
        },
        context_instance=RequestContext(request)
    )

def outside_spenders_redirect(request):
    return redirect("/outside-spenders/2014/")





@cache_control(no_cache=True)
def dynamic_ies(request):
    districts = District.objects.filter(outside_spending__gt=1000).order_by('state', 'office', 'office_district')
    candidates = Candidate_Overlay.objects.filter(total_expenditures__gt=1).select_related('district').order_by('name')
    outside_spenders = Committee_Overlay.objects.filter(total_indy_expenditures__gte=1000).order_by('name')
    
    return render_to_response('datapages/dynamic_ies.html', 
        {
        'STATE_LIST':STATE_LIST,
        'title':'Outside Expenditures',
        'explanatory_text':'Find and filter the latest independent expenditures reported. Only races and candidates that have reported independent expenditures of $1,000 or more are given as menu choices. For more, see a <a href="/about/#outside-spending">more detailed explanation</a>.<br>Also see a list of <a href="/outside-spenders/">all outside spending groups</a>.',
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
    committees=f1filer.objects.filter(receipt_dt__gte=month_ago).order_by('-receipt_dt')
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

def downloads_redirect(request):
    return redirect("/download-index/2016/")


def downloads(request, cycle):
    
    if not is_valid_four_digit_string_cycle(cycle):
        # should redirect, but for now:
        raise Http404

    other_year = None
    if cycle == '2016':
        other_year = '2014'
    elif cycle == '2014':
        other_year = '2016'
    cycle_list = [cycle_fake(cycle, "/download-index/%s/" % cycle), cycle_fake(other_year, "/download-index/%s/" % other_year)]
    
    title="Bulk Downloads" 
    update_time = get_update_time(BULK_EXPORT_KEY)

    return render_to_response('datapages/downloads.html',
        {
        'title':title,
        'cycle':cycle,
        'cycle_list':cycle_list,
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
    title="%s: details of filing #%s" % ( filing.committee_name, filing_num)
    
    if not filing.committee_name:
        try:
            committee = Committee_Overlay.objects.get(fec_id = filing.fec_id, cycle=filing.cycle)
            title="<a href=\"%s\">%s</a>: details of filing #%s" % (committee.get_absolute_url(), committee.name, filing_num)
        
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

""" Redirect to 2014 because these pages were only available for 2014 committees. """
@cache_page(LONG_CACHE_TIME)
def committee(request, slug, committee_id):
    return redirect("/committee/2014/%s/%s/" % (slug, committee_id))
    
    """ 
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
 """

@cache_page(1)
def committee_cycle(request, cycle, committee_id):
    
    if not is_valid_four_digit_string_cycle(cycle):
        # should redirect, but for now:
        raise Http404
    
    cycle_endpoints = get_cycle_endpoints(int(cycle))
    
    committee_overlay = get_object_or_404(Committee_Overlay, fec_id=committee_id, cycle=int(cycle))

    title = committee_overlay.name + " (%s cycle )" % (cycle)
    
    report_list = Committee_Time_Summary.objects.filter(com_id=committee_id, coverage_from_date__gte=cycle_endpoints['start'], coverage_from_date__lte=cycle_endpoints['end']).order_by('-coverage_through_date')


    end_of_coverage_date = committee_overlay.cash_on_hand_date
    recent_report_list = None

    if end_of_coverage_date:
        relevant_date = max(end_of_coverage_date, cycle_endpoints['start'])
        recent_report_list = new_filing.objects.filter(fec_id=committee_id, coverage_from_date__gte=relevant_date, coverage_to_date__lte=cycle_endpoints['end'], form_type__in=['F5A', 'F5', 'F5N', 'F24', 'F24A', 'F24N', 'F6', 'F6A', 'F6N']).exclude(is_f5_quarterly=True).exclude(is_superceded=True)
    else:
        recent_report_list = new_filing.objects.filter(fec_id=committee_id, coverage_from_date__gte=cycle_endpoints['start'], coverage_to_date__lte=cycle_endpoints['end'],  form_type__in=['F5A', 'F5', 'F5N', 'F24', 'F24A', 'F24N', 'F6', 'F6A', 'F6N']).exclude(is_f5_quarterly=True).exclude(is_superceded=True)

    independent_spending = Pac_Candidate.objects.filter(committee=committee_overlay, total_ind_exp__gte=5000, cycle=cycle).select_related('candidate')

    recent_ies = None
    if committee_overlay.total_indy_expenditures > 5000:
        recent_ies = SkedE.objects.filter(filer_committee_id_number=committee_id, expenditure_amount__gte=5000, superceded_by_amendment=False, expenditure_date_formatted__gte=cycle_endpoints['start'], expenditure_date_formatted__lte=cycle_endpoints['end']).select_related('candidate_checked').order_by('-expenditure_date_formatted')[:10]


    # figure out which cycles are available. The current one goes first, because it is being displayed.     
    cycle_values = Committee_Overlay.objects.filter(fec_id=committee_id).exclude(cycle=cycle)
    cycle_list = [committee_overlay] + list(cycle_values)

    return render_to_response('datapages/committee_cycle.html',
        {
        'title':title,
        'report_list':report_list,
        'recent_report_list':recent_report_list,
        'committee':committee_overlay,
        'independent_spending':independent_spending,
        'recent_ies':recent_ies,
        'cycle_list':cycle_list,
        'cycle':cycle,
        }, 
        context_instance=RequestContext(request)
    )
""" to be replaced with candidate_cycle """

@cache_page(LONG_CACHE_TIME)
def candidate(request, slug, candidate_id):
    # this form of url was used for 2014, so redirect there.
    return redirect("/candidate/2014/%s/%s/" % (slug, candidate_id))
    



@cache_page(LONG_CACHE_TIME)
def candidate_cycle(request, slug, candidate_id, cycle):
    if not is_valid_four_digit_string_cycle(cycle):
        raise Http404
    
    # figure out which cycles are available. The current one goes first, because it is being displayed.     
    cycles = Candidate_Overlay.objects.filter(fec_id=candidate_id)
    
    candidate_overlay = None
    try:
        candidate_overlay = cycles.get(cycle=cycle)
    except Candidate_Overlay.DoesNotExist:
        if len(cycles) > 0:
            candidate_overlay = cycles.order_by('-cycle')[0]
            return redirect("/candidate/%s/%s/%s/" % (candidate_overlay.cycle, slug, candidate_id))
        else:
            raise Http404
    
    other_cycles = cycles.exclude(cycle=cycle)
    cycle_list = [candidate_overlay] + list(other_cycles)
    cycle_endpoints = get_cycle_endpoints(int(cycle))
        
    title = "%s (%s) (%s cycle)" % (candidate_overlay.name, candidate_overlay.party, cycle)

    authorized_committee_list = Authorized_Candidate_Committees.objects.filter(candidate_id=candidate_id, cycle=cycle)
    committee_list = [x.get('committee_id') for x in authorized_committee_list.values('committee_id')]

    report_list = Committee_Time_Summary.objects.filter(com_id__in=committee_list, coverage_from_date__gte=cycle_endpoints['start'], coverage_through_date__lte=cycle_endpoints['end']).order_by('-coverage_through_date')


    end_of_coverage_date = None
    recent_report_list = None
    if report_list:
        end_of_coverage_date = report_list[0].coverage_through_date


    recent_report_total = 0
    if end_of_coverage_date:
        recent_report_list = new_filing.objects.filter(fec_id__in=committee_list, coverage_from_date__gte=end_of_coverage_date, coverage_to_date__lte=cycle_endpoints['end'], form_type__in=['F6', 'F6A', 'F6N']).exclude(is_superceded=True)
        if recent_report_list:
            recent_report_total = recent_report_list.aggregate(spending_total=Sum('tot_raised'))['spending_total']

    else:
        recent_report_list = new_filing.objects.filter(fec_id__in=committee_list, coverage_from_date__gte=cycle_endpoints['start'], coverage_to_date__lte=cycle_endpoints['end'], form_type__in=['F6', 'F6A', 'F6N']).exclude(is_superceded=True)


    # are their outside groups who've spent for/against this candidate? 
    outside_spenders = Pac_Candidate.objects.filter(candidate=candidate_overlay, cycle=cycle,  total_ind_exp__gte=1000).select_related('committee')

    recent_ies = None
    if outside_spenders:
        recent_ies = SkedE.objects.filter(candidate_checked=candidate_overlay, expenditure_amount__gte=5000, superceded_by_amendment=False, expenditure_date_formatted__gte=cycle_endpoints['start'], expenditure_date_formatted__lte=cycle_endpoints['end'] ).select_related('candidate_checked').order_by('-expenditure_date_formatted')[:10]



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
        'cycle_list':cycle_list,
        'current_cycle':cycle
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

@cache_control(no_cache=True)
def top_races(request, week_number): 
    week_start = get_week_start(int(week_number))
    week_start_formatted = week_start.strftime('%m/%d')
    week_end = get_week_end(int(week_number))
    week_end_formatted = week_end.strftime('%m/%d, %Y')
    period_start = week_start - datetime.timedelta(days=14)
    
    

    weeklysummaries = DistrictWeekly.objects.filter(cycle_week_number=week_number, outside_spending__gte=1000).order_by('-outside_spending')[:3]
    title = "Top races by outside spending, %s-%s" % (week_start_formatted, week_end_formatted)
    previous_week_number = None
    following_week_number = None
    if int(week_number) > 1:
        previous_week_number = int(week_number) - 1
    if int(week_number) < get_week_number(datetime.date.today()):
        following_week_number = int(week_number) + 1
    
    district_ids = weeklysummaries.values("district__pk")
    district_id_list = [str(x['district__pk']) for x in district_ids]
    district_list = ",".join(district_id_list)
    data_url = "http://realtime.influenceexplorer.com/api/districts-weekly/?week_start=%s&week_end=%s&districts=%s&format=json" % (int(week_number)-2, week_number, district_list)
    
    return render_to_response('datapages/top_races.html',
        {
        'title':title,
        'period_start': period_start,
        'week_start':week_start,
        'week_end':week_end,
        'weeklysummaries':weeklysummaries,
        'previous_week_number':previous_week_number,
        'following_week_number':following_week_number,
        'week_number':week_number,
        'data_url':data_url,
        }, 
        context_instance=RequestContext(request)
    )

@cache_control(no_cache=True)
def top_current_races(request): 
    week_number = get_week_number(datetime.date.today()) - 1
    week_start = get_week_start(int(week_number))
    week_start_formatted = week_start.strftime('%m/%d')
    week_end = get_week_end(int(week_number))
    week_end_formatted = week_end.strftime('%m/%d, %Y')
    previous_week_number = int(week_number) - 1
    following_week_number = int(week_number) + 1
    period_start = week_start - datetime.timedelta(days=14)

    weeklysummaries = DistrictWeekly.objects.filter(cycle_week_number=week_number, outside_spending__gt=1000).order_by('-outside_spending')[:3]
    title = "Top races by outside spending, %s-%s" % (week_start_formatted, week_end_formatted)
    
    district_ids = weeklysummaries.values("district__pk")
    district_id_list = [str(x['district__pk']) for x in district_ids]
    district_list = ",".join(district_id_list)
    data_url = "http://realtime.influenceexplorer.com/api/districts-weekly/?week_start=%s&week_end=%s&districts=%s&format=json" % (int(week_number)-2, week_number, district_list)
    
    return render_to_response('datapages/top_races.html',
        {
        'previous_week_number':previous_week_number,
        'following_week_number':following_week_number,
        'title':title,
        'period_start': period_start,
        'week_start':week_start,
        'week_end':week_end,
        'weeklysummaries':weeklysummaries,
        'week_number':week_number,
        'data_url':data_url,
        }, 
        context_instance=RequestContext(request)
    )


@cache_page(LONG_CACHE_TIME)
def election_calendar(request): 
    
    title = "2014 Cycle Election Calendar"
    return render_to_response('datapages/election_calendar.html',
        {
        'elections_by_day':elections_by_day,
        'title':title,
        }
    )

def chart_test(request, blog_or_feature):
    if not (blog_or_feature in ['feature', 'blog']):
        raise Http404
        
    return render_to_response('datapages/chart_test.html',
            {
            'blog_or_feature':blog_or_feature
            }
        )

def chart_listing(request):
    
    chart_list = []
    for key in chart_name_reference:
        value = chart_name_reference[key]
        value['race_id'] = key
        print value
        chart_list.append(value)
        
    chart_list.sort(key=lambda x: x['name'])
    return render_to_response('datapages/chart_listing.html',
            {
            'chart_list':chart_list,
            'type_list':['narrow', 'blog', 'feature']
            }
        )
                
def senate_races(request, blog_or_feature):
    if not (blog_or_feature in ['feature', 'blog', 'narrow']):
        raise Http404

    return render_to_response('datapages/senate_races.html',
            {
            'blog_or_feature':blog_or_feature,
            }, 
            context_instance=RequestContext(request)
        )



def roi_chart(request, blog_or_feature):
    if not (blog_or_feature in ['feature', 'blog', 'narrow']):
        raise Http404

    return render_to_response('datapages/roi_chart.html',
            {
            'blog_or_feature':blog_or_feature,
            }, 
            context_instance=RequestContext(request)
        )


def weekly_comparison(request, race_list, blog_or_feature):
    print "weekly comparison"
    if not (blog_or_feature in ['feature', 'blog', 'narrow']):
        raise Http404
    race_ids = race_list.split('-')
    if len(race_ids) == 0 or len(race_ids) > 6: 
        raise Http404
    race_id_text = ",".join(race_ids)
    
    chart_title = ""
    partisan_colors = 'false'
    
    try:
        chart_data = chart_name_reference[race_list]
        chart_title = chart_data['name']
        partisan_colors = chart_data['partisan']
    
    except KeyError:
    
        for i,id in enumerate(race_ids):
            try:
                series_name = weekly_dump_data_series[int(id)]['data_series_name']
                if i>0:
                    chart_title = chart_title + " and "
                chart_title = chart_title + series_name
            
            except IndexError:
                continue
        chart_title = chart_title + ", weekly"
    
    return render_to_response('datapages/comparisons_chart.html',
            {
            'race_id_text':race_id_text,
            'chart_title': chart_title,
            'blog_or_feature':blog_or_feature,
            'partisan_colors':partisan_colors,
            'data_source': '/static/data/weekly_ies.csv',
            #'data_source': '/static/realtimefec/js/weekly_ies.csv',
            'period_description':'previous seven days',
            'start_month':5,
            'start_year':2014,
            }, 
            context_instance=RequestContext(request)
        )

def weekly_comparison_cumulative(request, race_list, blog_or_feature):
    print "weekly comparison"
    if not (blog_or_feature in ['feature', 'blog', 'narrow']):
        raise Http404
    race_ids = race_list.split('-')
    if len(race_ids) == 0 or len(race_ids) > 6: 
        raise Http404
    race_id_text = ",".join(race_ids)

    chart_title = ""
    partisan_colors = 'false'

    try:
        chart_data = chart_name_reference[race_list]
        chart_title = chart_data['name']
        partisan_colors = chart_data['partisan']

    except KeyError:

        for i,id in enumerate(race_ids):
            try:
                series_name = weekly_dump_data_series[int(id)]['data_series_name']
                if i>0:
                    chart_title = chart_title + " and "
                chart_title = chart_title + series_name

            except IndexError:
                continue
        chart_title = chart_title + ", weekly"

    return render_to_response('datapages/comparisons_chart.html',
            {
            'race_id_text':race_id_text,
            'chart_title': chart_title,
            'blog_or_feature':blog_or_feature,
            'partisan_colors':partisan_colors,
            'data_source': '/static/data/weekly_ies_cumulative.csv',
            #'data_source': '/static/realtimefec/js/weekly_ies_cumulative.csv',
            'period_description':'cycle through date shown',
            'start_month':5,
            'start_year':2014,
            
            }, 
            context_instance=RequestContext(request)
        )


def contrib_comparison(request, race_list, blog_or_feature):
    print "weekly comparison"
    if not (blog_or_feature in ['feature', 'blog', 'narrow']):
        raise Http404
    race_ids = race_list.split('-')
    if len(race_ids) == 0 or len(race_ids) > 6: 
        raise Http404
    race_id_text = ",".join(race_ids)

    chart_title = ""
    partisan_colors = 'false'

    try:
        chart_data = chart_donor_name_reference[race_list]
        chart_title = chart_data['name']
        partisan_colors = chart_data['partisan']

    except KeyError:

        for i,id in enumerate(race_ids):
            try:
                series_name = weekly_dump_data_series[int(id)]['data_series_name']
                if i>0:
                    chart_title = chart_title + " and "
                chart_title = chart_title + series_name

            except IndexError:
                continue
        chart_title = chart_title + ", weekly"

    return render_to_response('datapages/comparisons_chart.html',
            {
            'race_id_text':race_id_text,
            'chart_title': chart_title,
            'blog_or_feature':blog_or_feature,
            'partisan_colors':partisan_colors,
            'data_source': '/static/data/weekly_superpac_donations.csv',
            'period_description':'previous seven days',
            'start_month':5,
            'start_year':2014,
            }, 
            context_instance=RequestContext(request)
        )

def contrib_comparison_cumulative(request, race_list, blog_or_feature):
    print "weekly comparison"
    if not (blog_or_feature in ['feature', 'blog', 'narrow']):
        raise Http404
    race_ids = race_list.split('-')
    if len(race_ids) == 0 or len(race_ids) > 6: 
        raise Http404
    race_id_text = ",".join(race_ids)

    chart_title = ""
    partisan_colors = 'false'

    try:
        chart_data = chart_donor_name_reference[race_list]
        chart_title = chart_data['name']
        partisan_colors = chart_data['partisan']

    except KeyError:

        for i,id in enumerate(race_ids):
            try:
                series_name = weekly_dump_data_series[int(id)]['data_series_name']
                if i>0:
                    chart_title = chart_title + " and "
                chart_title = chart_title + series_name

            except IndexError:
                continue
        chart_title = chart_title + ", weekly"

    return render_to_response('datapages/comparisons_chart.html',
            {
            'race_id_text':race_id_text,
            'chart_title': chart_title,
            'blog_or_feature':blog_or_feature,
            'partisan_colors':partisan_colors,
            'data_source': '/static/data/weekly_superpac_donations_cumulative.csv',
            'period_description':'cycle through date shown',
            'start_month':5,
            'start_year':2014,
            
            }, 
            context_instance=RequestContext(request)
        )
