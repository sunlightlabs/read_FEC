import django_filters

from datetime import date, timedelta
from fec_alerts.models import new_filing
from summary_data.models import Committee_Overlay, Authorized_Candidate_Committees, DistrictWeekly, District, Candidate_Overlay
from formdata.models import SkedE
from django.db.models import Q
from summary_data.utils.weekly_update_utils import get_week_number



class NFFilter(django_filters.FilterSet):
    
    # can create both ends of a range like this: 
    min_raised = django_filters.NumberFilter(name='tot_raised', lookup_type='gte')
    min_spent = django_filters.NumberFilter(name='tot_spent', lookup_type='gte')
    min_coh = django_filters.NumberFilter(name='coh_end', lookup_type='gte')

    
    filed_before = django_filters.DateFilter(name='filed_date', lookup_type='lte') 
    filed_after = django_filters.DateFilter(name='filed_date', lookup_type='gte') 
    

    class Meta:
        model = new_filing
        fields = ['fec_id', 'committee_name', 'filing_number', 'form_type', 'filed_date', 'coverage_from_date', 'coverage_to_date', 'is_superpac', 'committee_designation', 'committee_type', 'committee_slug', 'party', 'coh_end', 'new_loans', 'tot_raised', 'tot_spent', 'lines_present', 'is_superceded']
        

class COFilter(django_filters.FilterSet):

    # can create both ends of a range like this: 
    min_raised = django_filters.NumberFilter(name='total_receipts', lookup_type='gte')
    min_spent = django_filters.NumberFilter(name='total_disbursements', lookup_type='gte')
    min_coh = django_filters.NumberFilter(name='cash_on_hand', lookup_type='gte')

    class Meta:
        model = Committee_Overlay
        fields = ['fec_id', 'name', 'slug', 'cycle', 'term_class', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'cash_on_hand', 'cash_on_hand_date', 'ctype', 'political_orientation']



class OSFilter(django_filters.FilterSet):

    # can create both ends of a range like this: 
    min_ies = django_filters.NumberFilter(name='total_indy_expenditures', lookup_type='gte')

    class Meta:
        model = Committee_Overlay
        fields = ['fec_id', 'name', 'total_receipts', 'total_disbursements', 'outstanding_loans', 'ctype', 'total_indy_expenditures','ie_support_dems', 'ie_oppose_dems', 'ie_support_reps', 'ie_oppose_reps', 'political_orientation', 'political_orientation_verified', 'cycle']


class DistrictFilter(django_filters.FilterSet):
    
    class Meta:
        model = District
        fields = ['id', 'cycle', 'state', 'office', 'office_district', 'term_class', 'incumbent_name', 'incumbent_party', 'next_election_date', 'next_election_code', 'open_seat', 'candidate_raised', 'candidate_spending', 'outside_spending', 'total_spending', 'rothenberg_rating_id', 'rothenberg_rating_text']
    


class CandidateFilter(django_filters.FilterSet):

    class Meta:
        model = Candidate_Overlay
        fields = ['name', 'fec_id', 'pcc', 'party', 'is_incumbent', 'cycle', 'not_seeking_reelection', 'other_office_sought', 'other_fec_id', 'election_year', 'state', 'office', 'office_district', 'term_class', 'candidate_status', 'total_expenditures', 'expenditures_supporting', 'expenditures_opposing', 'total_receipts', 'total_contributions', 'total_disbursements', 'cash_on_hand', 'cash_on_hand_date']


    
class DWFilter(django_filters.FilterSet):
    
    week_start = django_filters.NumberFilter(name='cycle_week_number', lookup_type='gte')
    week_end = django_filters.NumberFilter(name='cycle_week_number', lookup_type='lte')
    

    class Meta:
        model = DistrictWeekly
        fields = ['start_date', 'end_date', 'cycle_week_number', 'outside_spending']
    

class SkedEFilter(django_filters.FilterSet):
    
    min_spent = django_filters.NumberFilter(name='expenditure_amount', lookup_type='gte')
    
    class Meta:
        model = SkedE
        fields=('form_type', 'candidate_id_checked', 'candidate_party_checked', 'candidate_office_checked', 'candidate_state_checked', 'candidate_district_checked', 'support_oppose_checked', 'payee_state', 'expenditure_date_formatted', 'expenditure_amount', 'filer_committee_id_number', 'district_checked')
        
def yearFilter(queryset, querydict):
    try:
        year=int(querydict['year_covered'])
        queryset = queryset.filter(Q(coverage_from_date__gte=date(year,1,1), coverage_to_date__lte=date(year,12,31)))
    
    except (KeyError, ValueError):
        pass
    return queryset
    

def DWDistrictFilter(queryset, querydict):
    try:
        district_list=querydict['districts']
        
        # if there's no commas, it's just a single district
        if district_list.find(',') < 0:
            queryset = queryset.filter(district__pk=district_list)
            
        # if there's a comma, it's a comma-delimited list
        else:
            district_ids = district_list.split(',')
            queryset = queryset.filter(district__pk__in=district_ids)
    
    except KeyError:
        pass
        
    return queryset

def candidatedistrictFilter(queryset, querydict):
    try:
        id=int(querydict['district'])
        queryset = queryset.filter(district__pk=id)

    except (KeyError, ValueError):
        pass
        
    return queryset

def districtIDFilter(queryset, querydict):
    try:
        id=int(querydict['pk'])
        queryset = queryset.filter(pk=id)

    except (KeyError, ValueError):
        pass
    return queryset

def weekFilter(queryset, querydict):
    try:
        week=querydict['week']

        # if there's no commas, it's just a single district
        if week.upper() == "NOW":
            queryset = queryset.filter(cycle_week_number = get_week_number(date.today()) )
        if week.upper() == "LAST":
            queryset = queryset.filter(cycle_week_number = get_week_number(date.today())-1 )


    except KeyError:
        pass

    return queryset

def periodTypeFilter(queryset, querydict):
    try:
        period_type=querydict['period_type']
        if period_type.startswith('Q'):
            if period_type == 'Q1':
                queryset = queryset.filter(coverage_from_date__month=1, coverage_from_date__day=1, coverage_to_date__month=3, coverage_to_date__day=31)
            elif period_type == 'Q2':
                queryset = queryset.filter(coverage_from_date__month=4, coverage_from_date__day=1, coverage_to_date__month=6, coverage_to_date__day=30)
            elif period_type == 'Q3':
                queryset = queryset.filter(coverage_from_date__month=7, coverage_from_date__day=1, coverage_to_date__month=9, coverage_to_date__day=30)
            elif period_type == 'Q4':
                queryset = queryset.filter(coverage_from_date__month=10, coverage_from_date__day=1, coverage_to_date__month=12, coverage_to_date__day=31)

        elif period_type.startswith('M'):
                        
            if period_type == 'M1':
                queryset = queryset.filter(coverage_from_date__month=1, coverage_from_date__day=1, coverage_to_date__month=1, coverage_to_date__day=31)
            elif period_type == 'M2':
                # leap years! 
                queryset = queryset.filter(Q(coverage_from_date__month=2, coverage_from_date__day=1, coverage_to_date__month=2, coverage_to_date__day=28)|Q(coverage_from_date__month=2, coverage_from_date__day=1, coverage_to_date__month=2, coverage_to_date__day=29))
            elif period_type == 'M3':
                queryset = queryset.filter(coverage_from_date__month=3, coverage_from_date__day=1, coverage_to_date__month=3, coverage_to_date__day=31)
            elif period_type == 'M4':
                queryset = queryset.filter(coverage_from_date__month=4, coverage_from_date__day=1, coverage_to_date__month=4, coverage_to_date__day=30)
            elif period_type == 'M5':
                queryset = queryset.filter(coverage_from_date__month=5, coverage_from_date__day=1, coverage_to_date__month=5, coverage_to_date__day=31)
            elif period_type == 'M6':
                queryset = queryset.filter(coverage_from_date__month=6, coverage_from_date__day=1, coverage_to_date__month=6, coverage_to_date__day=30)
            elif period_type == 'M7':
                queryset = queryset.filter(coverage_from_date__month=7, coverage_from_date__day=1, coverage_to_date__month=7, coverage_to_date__day=31)
            elif period_type == 'M8':
                queryset = queryset.filter(coverage_from_date__month=8, coverage_from_date__day=1, coverage_to_date__month=8, coverage_to_date__day=31)
            elif period_type == 'M9':
                queryset = queryset.filter(coverage_from_date__month=9, coverage_from_date__day=1, coverage_to_date__month=9, coverage_to_date__day=30)
            elif period_type == 'M10':
                queryset = queryset.filter(coverage_from_date__month=10, coverage_from_date__day=1, coverage_to_date__month=10, coverage_to_date__day=31)
            elif period_type == 'M11':
                queryset = queryset.filter(coverage_from_date__month=11, coverage_from_date__day=1, coverage_to_date__month=11, coverage_to_date__day=30)
            elif period_type == 'M12':
                queryset = queryset.filter(coverage_from_date__month=12, coverage_from_date__day=1, coverage_to_date__month=12, coverage_to_date__day=31)
                
        elif period_type == 'PRE':
            queryset = queryset.filter(Q(coverage_from_date=date(2014,10,1), coverage_to_date=date(2014,10,15)))
        elif period_type == 'POS':
            queryset = queryset.filter(Q(coverage_from_date=date(2014,10,16), coverage_to_date=date(2014,11,24)))
        elif period_type == 'EOY':
            queryset = queryset.filter(coverage_to_date=date(2014,12,31))
        
        
        elif period_type.startswith('S'):
            if period_type == 'S1':
                queryset = queryset.filter(coverage_from_date__month=1, coverage_from_date__day=1, coverage_to_date__month=6, coverage_to_date__day=30)
            elif period_type == 'S2':
                queryset = queryset.filter(coverage_from_date__month=7, coverage_from_date__day=1, coverage_to_date__month=12, coverage_to_date__day=31)
        
    except KeyError:
        pass
    return queryset

def reportTypeFilter(queryset, querydict):
    try:
        report_type=querydict['report_type']
        if report_type == 'monthly':
            queryset = queryset.filter(form_type__in=['F3X', 'F3XN', 'F3XA', 'F3', 'F3A', 'F3N', 'F3P', 'F3PA', 'F3PN'])
            
        elif report_type == 'ies':
            queryset = queryset.filter(form_type__in=['F5', 'F5N', 'F5A', 'F24', 'F24A', 'F24N'])
            
        elif report_type == 'F6':
            queryset = queryset.filter(form_type__in=['F6', 'F6N', 'F6A'])
            
        elif report_type == 'F9':
            queryset = queryset.filter(form_type__in=['F9', 'F9N', 'F9A'])
            
        elif report_type == 'F2':
            queryset = queryset.filter(form_type__in=['F2', 'F2N', 'F2A'])
            
        elif report_type == 'F1':
            queryset = queryset.filter(form_type__in=['F1', 'F1N', 'F1A'])

        elif report_type == 'F13':
            queryset = queryset.filter(form_type__in=['F13', 'F13N', 'F13A'])
            
        elif report_type == 'F4':
            queryset = queryset.filter(form_type__in=['F4', 'F4N', 'F4A'])                        
    except KeyError:
        pass
    
    return queryset
                        
def orderingFilter(queryset, querydict, fields):
    """
    Only works if the ordering hasn't already been set. Which it hasn't, but... 
    """
    try:
        ordering=querydict['ordering']
        if ordering.lstrip('-') in fields:
            orderlist = [ordering]
            queryset = queryset.order_by(*orderlist)
        
    except KeyError:
        pass
    
    return queryset
    
def committeeSearchSlow(queryset, querydict):
    """
    Table scan--maybe some sorta dropdown in front of this? 
    """
    try:
        search_term = querydict['search_term']
        queryset = queryset.filter(committee_name__icontains=search_term)

    except KeyError:
        pass
    return queryset

def candidateidSearch(queryset, querydict):
    try:
        candidate_id = querydict['candidate_id']
        authorized_committee_list = Authorized_Candidate_Committees.objects.filter(candidate_id=candidate_id)
        committee_list = [x.get('committee_id') for x in authorized_committee_list.values('committee_id')]
        queryset = queryset.filter(fec_id__in=committee_list)

    except KeyError:
        pass
    return queryset
        
def filingTimeFilter(queryset, querydict):
    try:
        time_range=querydict['time_range']
        if time_range == 'day':
            today = date.today()
            queryset = queryset.filter(filed_date=today)
        elif time_range == 'week':
            today = date.today()
            one_week_ago = today-timedelta(days=7)
            queryset = queryset.filter(filed_date__gte=one_week_ago)
        elif time_range == '2014_cycle':
            queryset = queryset.filter(filed_date__gte=date(2013,1,1), filed_date__lte=date(2014,12,31))
        elif time_range == '2016_cycle':
            queryset = queryset.filter(filed_date__gte=date(2015,1,1), filed_date__lte=date(2016,12,31))
    except KeyError:
        pass
    return queryset

# create a phony keyword committee class that is just a list of committee types allowed
# so superpacs would be 'UO' -- but if we wanted to included hybrids, it would be 'UOVW'
def multiCommitteeTypeFilter(queryset, querydict):
    try:
        committee_class = querydict['committee_class']
        committee_class = committee_class.upper()
        if committee_class == 'J':
            queryset = queryset.filter(committee_designation=committee_class)
        elif committee_class == 'L':
            # a D commmittee type is a delegate, so use L instead.
            queryset = queryset.filter(committee_designation='D')
        else:
            committee_type_list = list(committee_class)
            queryset = queryset.filter(committee_type__in=committee_type_list)
        
    except KeyError:
        pass
        
    return queryset

# variant with different name for committee type.
def multiCTypeFilter(queryset, querydict):
    try:
        committee_class = querydict['committee_class']
        committee_class = committee_class.upper()
        if committee_class == 'J':
            queryset = queryset.filter(designation=committee_class)
        elif committee_class == 'L':
            # a D commmittee type is a delegate, so use L instead.
            queryset = queryset.filter(designation='D')
        else:
            committee_type_list = list(committee_class)
            queryset = queryset.filter(ctype__in=committee_type_list)

    except KeyError:
        pass

    return queryset
    
def candidateCommitteeSearchSlow(queryset, querydict):
    """
    Table scan--maybe some sorta dropdown in front of this? 
    """
    try:
        search_term = querydict['search_term']
        queryset = queryset.filter(Q(name__icontains=search_term)|Q(curated_candidate__name__icontains=search_term))
        
    except KeyError:
        pass
    return queryset
