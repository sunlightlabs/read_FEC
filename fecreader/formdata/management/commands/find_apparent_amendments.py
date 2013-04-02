from django.core.management.base import BaseCommand, CommandError
from formdata.models import Filing_Header


class Command(BaseCommand):
    help = "Find stuff that looks like an amendment, but isn't marked as such"
    requires_model_validation = False
    """
    #  select count(*), raw_filer_id, coverage_from_date, coverage_through_date, form from formdata_filing_header where is_amended=False and form not in ('F24A', 'F6', 'F5') and not coverage_from_date is null group by raw_filer_id, coverage_from_date, coverage_through_date, form order by count(*) desc;
    
    #C30001028 : ( american future fund) filings: 759555, 795560, 759586, 759598,   
    
    # AFF is a pretty bad offender here. Maybe ignore F9's altogether? 
    
    
    fec_reader=# select filing_number, coverage_from_date, coverage_through_date from formdata_filing_header where raw_filer_id = 'C00161901' and coverage_from_date = '2011-07-01';
     filing_number | coverage_from_date | coverage_through_date 
    ---------------+--------------------+-----------------------
            741973 | 2011-07-01         | 2011-07-31
            742189 | 2011-07-01         | 2011-07-31
            
            Hmm, but the first now appears missing on the server? 
            
            http://query.nictusa.com/cgi-bin/dcdev/forms/C00161901/741973/
    
    """