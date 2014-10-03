#!/bin/bash

# This doesn't actually get the webk file but the campaign and committee report by report summary file. 

datadir=/projects/realtimefec/src/realtimefec/fecreader/ftpdata/data/


# http://fec.gov/data/Form1Filer.do?format=csv

for year in  '14'
do
    curl -o $datadir/$year/Form1Filer_$year.csv "http://www.fec.gov/data/Form1Filer.do?format=csv&election_yr=20$year"
    
    echo "Running command: curl -o $datadir/$year/Form1Filer_$year.csv \"http://www.fec.gov/data/Form1Filer.do?format=csv&election_yr=20$year\""
    
done