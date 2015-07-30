#!/bin/bash
NAME=realtimefec
PROJ=fecreader

# run the import
source /projects/$NAME/virt/bin/activate

/projects/$NAME/src/$NAME/$PROJ/manage.py mark_amended_skede_lines
/projects/$NAME/src/$NAME/$PROJ/manage.py set_candidate_pac
/projects/$NAME/src/$NAME/$PROJ/manage.py make_candidate_os_aggregates
/projects/$NAME/src/$NAME/$PROJ/manage.py update_race_aggregates
/projects/$NAME/src/$NAME/$PROJ/manage.py update_all_candidate_times
#/projects/$NAME/src/$NAME/$PROJ/manage.py set_weekly_spending
/projects/$NAME/src/$NAME/$PROJ/manage.py update_committee_os_totals
/projects/$NAME/src/$NAME/$PROJ/manage.py remove_blacklisted
