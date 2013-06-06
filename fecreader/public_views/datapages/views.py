
from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection

from race_curation.utils.senate_crosswalk import senate_crosswalk

# get not null senate ids. 
senate_ids =  [ senator['fec_id'] for senator in senate_crosswalk if senator['fec_id'] ]

def current_senators(request):

    title="Senate Fundraising Summary"
    explanatory_text="Quarterly fundraising totals are based on money raised and spent by a legislator's principal campaign committee. Money raised by a leadership PAC is not included, unless it was transferred to a principal campaign committee during this period "

    # Give up on ORM for data; we're not willing to enforce all the relationships required for them
    
    cursor = connection.cursor()

    subquery = """(select fec_id from race_curation_candidate_overlay where cand_ici = 'I' and office = 'S';)"""
    
    cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
    row = cursor.fetchone()
    
    return render_to_response('datapages/legislator_list.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        }
    )
