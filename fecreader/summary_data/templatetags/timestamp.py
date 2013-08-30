# todo: generalize this. Used to only be one timestamp... 

from django.template import Library
from summary_data.utils.update_utils import get_update_time
from django.conf import settings

FILING_SCRAPE_KEY = settings.FILING_SCRAPE_KEY
COMMITTEES_SCRAPE_KEY  = settings.COMMITTEES_SCRAPE_KEY
BULK_EXPORT_KEY  = settings.BULK_EXPORT_KEY
register = Library()


@register.inclusion_tag('datapages/templatetag_templates/update_time.html')  
def timestamp_filings():
    most_recent_scrape = get_update_time(FILING_SCRAPE_KEY)
    return { 'most_recent_scrape': most_recent_scrape }
    
@register.inclusion_tag('datapages/templatetag_templates/update_time.html')  
def timestamp_committees():
    most_recent_scrape = get_update_time(COMMITTEES_SCRAPE_KEY)
    return { 'most_recent_scrape': most_recent_scrape }
    
@register.inclusion_tag('datapages/templatetag_templates/update_time.html')  
def timestamp_export():
    most_recent_scrape = get_update_time(BULK_EXPORT_KEY)
    return { 'most_recent_scrape': most_recent_scrape }