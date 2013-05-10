import re

from formdata.utils.form_mappers import *

from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing
from parsing.read_FEC_settings import FILECACHE_DIRECTORY
from formdata.models import Filing_Header

# load up a form parser
fp = form_parser()

filing_num = 708753

f1 = filing(filingnum, read_from_cache=True, write_to_cache=True)



a = re.compile(r'SA*', re.I)

rows = f1.get_rows(a)

# parse a row
parsed_row = fp.parse_form_line(rows[0], version)
print parsed_row

# parsed_row = {'conduit_zip': '', 'back_reference_sched_name': '', 'donor_candidate_prefix': '', 'contribution_aggregate': '250.00', 'donor_committee_name': '', 'contributor_street_2': '', 'donor_candidate_suffix': '', 'contributor_organization_name': '', 'contributor_suffix': '', 'contributor_state': 'TX', 'donor_committee_fec_id': '', 'entity_type': 'IND', 'donor_candidate_state': '', 'donor_candidate_district': '', 'contributor_prefix': '', 'contributor_last_name': 'Acton', 'donor_candidate_middle_name': '', 'transaction_id': 'SA11AI.30102', 'contribution_date': '20101021', 'contributor_occupation': '', 'filer_committee_id_number': 'C00460808', 'donor_candidate_last_name': '', 'conduit_street2': '', 'conduit_street1': '', 'contributor_city': 'Dallas', 'donor_candidate_first_name': '', 'contribution_purpose_descrip': '', 'election_code': 'G2010', 'donor_candidate_office': '', 'memo_text_description': '', 'donor_candidate_fec_id': '', 'form_type': 'SA11AI', 'contributor_first_name': 'Robert', 'contribution_purpose_code': '', 'election_other_description': '', 'conduit_name': '', 'contribution_amount': '150.00', 'conduit_city': '', 'contributor_employer': '', 'back_reference_tran_id_number': '', 'contributor_street_1': '6407 Meadow Road', 'conduit_state': '', 'reference_code': '', 'memo_code': '', 'contributor_zip': '752305142', 'contributor_middle_name': ''}

# can we save it? 
from formdata.utils.form_mappers import *
from formdata.models import Filing_Header


header = Filing_Header.objects.get(filing_number=708753)
parsed_row['filing_number'] = 708753
parsed_row['header'] = header

create_skeda_from_dict(parsed_row)