#!/bin/bash
NAME=realtimefec
PROJ=fecreader


source /projects/$NAME/virt/bin/activate
/projects/$NAME/src/$NAME/$PROJ/manage.py scrape_new_filers
