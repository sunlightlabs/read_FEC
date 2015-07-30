#!/bin/bash
NAME=realtimefec
PROJ=fecreader

source /projects/$NAME/virt/bin/activate
/projects/$NAME/src/$NAME/$PROJ/manage.py set_roi
/projects/$NAME/src/$NAME/$PROJ/manage.py audit_results
/projects/$NAME/src/$NAME/$PROJ/manage.py regen_results
/projects/$NAME/src/$NAME/$PROJ/manage.py write_roi_files
/projects/$NAME/src/$NAME/$PROJ/manage.py regen_roi
cp /mnt/regular_export/roi.csv /projects/realtimefec/src/realtimefec/fecreader/static-root/data/

