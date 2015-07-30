#!/bin/bash
NAME=realtimefec
PROJ=fecreader

source /projects/$NAME/virt/bin/activate
/projects/$NAME/src/$NAME/$PROJ/manage.py mark_superceded_body_rows
/projects/$NAME/src/$NAME/$PROJ/manage.py update_dirty_committee_times
/projects/$NAME/src/$NAME/$PROJ/manage.py process_skede_lines
