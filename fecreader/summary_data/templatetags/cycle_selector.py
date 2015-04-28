from django.template import Library, Variable

register = Library()

@register.inclusion_tag('datapages/templatetag_templates/cycle_selector.html')  
def cycle_select_block(cycles):
    selected_cycle = None
    if cycles:
        selected_cycle = cycles[0]
        # allow years to appear twice in the cycle list without freaking out. 
        # sort the list after we're done so it appears sorted in the select list
        cycles = sorted(list(set(cycles)))
    display = len(cycles) > 0
    is_selectable = len(cycles) > 1
    
    print "\n\n\n\n\n\n\nCYCLE SELECTOR\n\n\n\n\n"
    return { 'cycles': cycles, 'selected_cycle':selected_cycle, 'display':display, 'is_selectable':is_selectable }