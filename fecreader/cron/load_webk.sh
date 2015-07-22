#!/bin/bash
NAME=realtimefec
PROJ=fecreader

# grab the files:
source /projects/realtimefec/src/realtimefec/fecreader/ftpdata/shellscripts/get_webk.sh
source /projects/realtimefec/src/realtimefec/fecreader/ftpdata/shellscripts/get_f1_filers.sh
# run the import
source /projects/$NAME/virt/bin/activate
/projects/$NAME/src/$NAME/$PROJ/manage.py load_webk
/projects/$NAME/src/$NAME/$PROJ/manage.py remove_blacklisted
/projects/$NAME/src/$NAME/$PROJ/manage.py update_paper_committee_times
/projects/$NAME/src/$NAME/$PROJ/manage.py import_f1_filers
