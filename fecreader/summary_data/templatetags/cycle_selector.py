from django.template import Library, Variable

register = Library()


# This requires that any list we send to this templatetag has objects with a 
# cycle attribute and a get_absolute_url --which seems reasonable. 
def get_cycle_details(object):
    return {'cycle':object.cycle, 'url':object.get_absolute_url()}

@register.inclusion_tag('datapages/templatetag_templates/cycle_selector.html')  
def cycle_select_block(cycled_object_list):
    selected_cycle = None
    cycles = []
    selected_cycle_object = None
    if cycled_object_list:
        selected_cycle_object = get_cycle_details(cycled_object_list[0])
        
        for this_cycled_object in cycled_object_list:
            cycles.append(get_cycle_details(this_cycled_object))
        # sort the list after we're done so it appears sorted in the select list
        cycles = sorted(cycles)
    display = len(cycles) > 0
    is_selectable = len(cycles) > 1
    
    print cycles
    return { 'cycles': cycles, 'selected_cycle_object':selected_cycle_object, 'display':display, 'is_selectable':is_selectable }