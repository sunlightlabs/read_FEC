## Utils to handle common date / cycle manipulation.
## cycles are stored as 4-digit *strings*.
## this is for 2-year cycle...

from django.conf import settings

# Warn about this
try:
    current_cycle = settings.CURRENT_CYCLE
    active_cycles = settings.ACTIVE_CYCLES
except AttributeError:
    raise Exception("Make sure to define CURRENT CYCLE and ACTIVE CYCLES in the settings file. Cycles are given as 4-digit strings. ")


def get_cycle_from_date(date):
    # Should work for a date or datetime
    if not date:
        return None
    else:
        year = date.year
        if year%2 == 1:
            return str(year+1)
        else:
            return str(year)

def is_current_cycle(date):
    # Should work for a date or datetime
    return get_cycle_from_date == current_cycle

def is_active_cycle(date):
    # Should work for a date or datetime
    return get_cycle_from_date in active_cycles


        