#!/bin/bash

# This doesn't actually get the webk file but the campaign and committee report by report summary file. 

datadir=/projects/realtimefec/src/realtimefec/fecreader/ftpdata/data/

for year in  '14'
do
    for type in 'HOUSE_SENATE' 'INDEPENDENT_EXPENDITURE' 'PAC' 'PARTY' 'PRESIDENTIAL'
    do
        curl -o $datadir/$year/ccsummary_$type$year.csv "http://www.fec.gov/data/CampaignAndCommitteeSummary.do?format=csv&election_yr=20$year&fil_typ=$type"
        echo "Running command: curl -o $datadir/$year/ccsummary_$type$year.csv \"http://www.fec.gov/data/CampaignAndCommitteeSummary.do?format=csv&election_yr=20$year&fil_typ=$type\""
        sleep 1
        
    done
    echo "done"
done
