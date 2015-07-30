#!/bin/bash
NAME=realtimefec
PROJ=fecreader

# some processes to fix up sked e lines that have missing data
# probably because something wasn't in the system initially

source /projects/$NAME/virt/bin/activate
/projects/$NAME/src/$NAME/$PROJ/manage.py add_committees_to_skede
/projects/$NAME/src/$NAME/$PROJ/manage.py match_unmatched_skede
# /projects/$NAME/src/$NAME/$PROJ/manage.py regen_competitive_primaries
# /projects/$NAME/src/$NAME/$PROJ/manage.py set_next_election_dates
