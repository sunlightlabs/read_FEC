#!/bin/bash
NAME=realtimefec
PROJ=fecreader

# grab the files:
source /projects/realtimefec/src/realtimefec/fecreader/ftpdata/shellscripts/get_summary_ftp_files.sh
# run the import
psql -U realtimefec -d rtfc -f /projects/realtimefec/src/realtimefec/fecreader/ftpdata/sqlscripts/reload_ftp_summarydata_14.sql
psql -U realtimefec -d rtfc -f /projects/realtimefec/src/realtimefec/fecreader/ftpdata/sqlscripts/reload_ftp_summarydata_16.sql


# add new committees. This is non-destructive, and doesn't update. 
source /projects/$NAME/virt/bin/activate
/projects/$NAME/src/$NAME/$PROJ/manage.py add_committees
/projects/$NAME/src/$NAME/$PROJ/manage.py add_candidates
/projects/$NAME/src/$NAME/$PROJ/manage.py pop_auth_committees
/projects/$NAME/src/$NAME/$PROJ/manage.py set_committee_candidate_linkage
# This doesn't set missing filing slugs for filings before committee was created.
# /projects/$NAME/src/$NAME/$PROJ/manage.py set_weekly_spending --all
