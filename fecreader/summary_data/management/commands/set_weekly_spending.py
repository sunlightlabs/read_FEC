from optparse import make_option
from datetime import date

from django.core.management.base import BaseCommand, CommandError

from summary_data.utils.weekly_update_utils import summarize_week, get_week_number

class Command(BaseCommand):
    help = """Set weekly spending by district. 
            By default just calculates the current week. 
            Use the --all option to calculate all weeks."""
    requires_model_validation = False
    
    option_list = BaseCommand.option_list + (
            make_option('--all',
                action='store_true',
                dest='run_all',
                default=False,
                help='Summarize all weeks, not just the current one'),
            )
    
    def handle(self, *args, **options):
        current_week_number = get_week_number(date.today())
        week_list = [current_week_number]
        if options['run_all']:
            week_list = range(1,current_week_number+1)
        
        for week_number in week_list:
            print "Summarizing week %s" % (week_number)
            summarize_week(week_number)
        
