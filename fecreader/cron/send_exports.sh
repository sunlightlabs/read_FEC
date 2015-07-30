#!/bin/bash
NAME=realtimefec
PROJ=fecreader

source /projects/$NAME/virt/bin/activate
/projects/$NAME/src/$NAME/$PROJ/manage.py export_bulk_files_to_s3
/projects/$NAME/src/$NAME/$PROJ/manage.py export_summary_files_to_s3
/projects/$NAME/src/$NAME/$PROJ/manage.py regen_overview
# /projects/$NAME/src/$NAME/$PROJ/manage.py write_senate_district_csv
