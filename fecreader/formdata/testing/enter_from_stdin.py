# setup
import sys

from django.core.management import setup_environ
sys.path.append('/Users/jfenton/github-whitelabel/read_FEC/fecreader/fecreader/')
sys.path.append('/Users/jfenton/github-whitelabel/read_FEC/fecreader/')

import settings
setup_environ(settings)

## Erase all rows -- run before testing

from django.db import connection, transaction
from cStringIO import StringIO

cursor = connection.cursor()

cols = ['back_reference_sched_name', 'back_reference_tran_id_number', 'conduit_city', 'conduit_name', 'conduit_state', 'conduit_street1', 'conduit_street2', 'conduit_zip', 'contribution_aggregate', 'contribution_amount', 'contribution_date', 'contribution_date_formatted', 'contribution_purpose_code', 'contribution_purpose_descrip', 'contributor_city', 'contributor_employer', 'contributor_first_name', 'contributor_last_name', 'contributor_middle_name', 'contributor_name', 'contributor_occupation', 'contributor_organization_name', 'contributor_prefix', 'contributor_state', 'contributor_street_1', 'contributor_street_2', 'contributor_suffix', 'contributor_zip', 'donor_candidate_district', 'donor_candidate_fec_id', 'donor_candidate_first_name', 'donor_candidate_last_name', 'donor_candidate_middle_name', 'donor_candidate_name', 'donor_candidate_office', 'donor_candidate_prefix', 'donor_candidate_state', 'donor_candidate_suffix', 'donor_committee_fec_id', 'donor_committee_name', 'election_code', 'election_other_description', 'entity_type', 'filer_committee_id_number', 'filing_number', 'form_type', 'header_id', 'memo_code', 'memo_text_description', 'reference_code', 'superceded_by_amendment', 'transaction_id']




cmd = """||||||||455.3|50.0|20111001|2011-10-01 00:00:00|||College Place|Fluor|Richard|Corson|A||Cook||Mr.|WA|228 W Whitman Dr|||99324|||||||||||||P2012||IND|C00495820|767168|SA17A|339||| ||0857493
||||||||245.12|25.0|20111001|2011-10-01 00:00:00|||Denton|Walmart DC 6068|Henry|Hilton|William||Receiving||Rev.|TX|327 Withers St Apt 20||Jr|762013266|||||||||||||P2012||IND|C00495820|767168|SA17A|339||| ||0857494
||||||||1500.0|1000.0|20111001|2011-10-01 00:00:00|||Hico|Talsma Dairy|Anastasia|Thiele-Talsma|||Farmer|||TX|2574 County Rd 211|||764573341|||||||||||||P2012||IND|C00495820|767168|SA17A|339||| ||0857497
||||||||250.48|50.0|20111001|2011-10-01 00:00:00|||Leander|Self|Roger|Boley|J||consultant||Mr.|TX|1113 Calistoga Dr|||786412559|||||||||||||P2012||IND|C00495820|767168|SA17A|339||| ||0857526
||||||||230.0|45.0|20111001|2011-10-01 00:00:00|||Madera|Cargill Meat Solutions|David|Calderon|||Technical Services Technician|||CA|28545 Ward St|||936385922|||||||||||||P2012||IND|C00495820|767168|SA17A|339||| ||0857531
||||||||1268.13|64.0|20111001|2011-10-01 00:00:00|||Redmond|None|John|Stephens|||None|||WA|16095 Cleveland St Apt 620|||980524321|||||||||||||P2012||IND|C00495820|767168|SA17A|339||| ||0857534
||||||||1000.0|500.0|20111001|2011-10-01 00:00:00|||Tennille|US Air Force|Khalil|Chamma|||tactical air control party|||GA|115 W Adams St|||310891402|||||||||||||P2012||IND|C00495820|767168|SA17A|339||| ||0857538
||||||||603.6|201.2|20111001|2011-10-01 00:00:00|||Los Angeles|Digital Domain|Casey|Benn|C.||Digital Animator|||CA|3988 Moore St Apt 1|||900664194|||||||||||||P2012||IND|C00495820|767168|SA17A|339||| ||0857539
||||||||729.03|100.0|20111001|2011-10-01 00:00:00|||Llano|Liberty|Robert|McDonald|B.||Mother|||TX|1406 Ash St|||786432810|||||||||||||P2012||IND|C00495820|767168|SA17A|339||| ||0857543
||||||||319.58|50.0|20111001|2011-10-01 00:00:00|||Kalamazoo|Samuel Mancinos|Larry|Willis|||Food Service|||MI|2921 Danford Creek Dr Apt 2A||Jr.|490092028|||||||||||||P2012||IND|C00495820|767168|SA17A|339||| ||0857548
\.
"""

buf = StringIO()
buf.write(cmd)
length = buf.tell()
# have to move back to the start of the buffer
buf.seek(0)
cursor.copy_from(buf, 'formdata_skeda', sep='|', size=length, columns=cols, null="")

status = cursor.statusmessage
if status:
    print "Result: %s" % status
transaction.commit_unless_managed()