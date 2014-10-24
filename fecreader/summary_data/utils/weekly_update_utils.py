from datetime import date,timedelta

from django.db.models import Sum

from formdata.models import SkedE
from summary_data.models import District, DistrictWeekly

cycle_iso_start = date(2012,12,31)

def get_week_number(thedate):
    """ helper function that returns the week number for the 2014 cycle """
    (year, week, day) = thedate.isocalendar()
    return (52*(year-2013)) + week

def get_week_end(week_number):
    # last sunday of the week
    return (cycle_iso_start + timedelta(days=(week_number)*7-1))

def get_week_start(week_number):
    # first monday of the week
    return (cycle_iso_start + timedelta(days=(week_number-1)*7))
    
def summarize_week(week_number):
    week_start = get_week_start(week_number)
    week_end = get_week_end(week_number)
    
    # set it one at a time by race
    # it's slower, but if we aggregate we might fail to update a race that has been zeroed out.
    for district in District.objects.all():
        
        # we're ignoring coordinated communications this way, fwiw
        weekly_ies = SkedE.objects.filter(district_checked=district, superceded_by_amendment=False, expenditure_date_formatted__gte=week_start, expenditure_date_formatted__lte=week_end)
        outside_spending = weekly_ies.aggregate(tot_spending=Sum('expenditure_amount'))['tot_spending']
        total_spending = outside_spending
        
        obj, created = DistrictWeekly.objects.get_or_create(district=district, cycle_week_number=week_number)
        # reset all this stuff--we may change the dates at some point
        obj.start_date = week_start 
        obj.end_date = week_end
        obj.outside_spending = outside_spending
        obj.total_spending = total_spending
        
        obj.save()
        #print "Total amount spent in %s for week %s (%s-%s): %s" % (district, week_number, week_start, week_end, total_spending)
    
    
def summarize_week_queryset(week_number, skede_queryset):
    week_start = get_week_start(week_number)
    week_end = get_week_end(week_number)
    
    outside_spending = skede_queryset.filter(expenditure_date_formatted__gte=week_start, expenditure_date_formatted__lte=week_end).aggregate(tot_spending=Sum('expenditure_amount'))['tot_spending']
    
    return outside_spending

def summarize_week_queryset_cumulative(week_number, skede_queryset):
    week_end = get_week_end(week_number)

    outside_spending = skede_queryset.filter(expenditure_date_formatted__gt=cycle_iso_start, expenditure_date_formatted__lte=week_end).aggregate(tot_spending=Sum('expenditure_amount'))['tot_spending']

    return outside_spending
        
    