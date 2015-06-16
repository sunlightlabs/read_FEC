### Processing flags on new_filing  

    ### processing status notes
    filing_is_downloaded = models.NullBooleanField(default=False)
    header_is_processed = models.NullBooleanField(default=False)
    previous_amendments_processed = models.NullBooleanField(default=False)
    new_filing_details_set = models.NullBooleanField(default=False)
    data_is_processed = models.NullBooleanField(default=False)
    
    ## New # Have the body rows in superceded filings been marked as amendments? 
    body_rows_superceded = models.NullBooleanField(default=False)
    # Have we added data to skede stuff ? 
    ie_rows_processed = models.NullBooleanField(default=False)


### Cron jobs

#### first step 

	16,46 * * * * /projects/realtimefec/bin/load_step_1.sh 2>&1 >> /mnt/cron/load_1.log
  
  ---
	 $ cat /projects/realtimefec/bin/load_step_1.sh
	 #!/bin/bash
	 NAME=realtimefec
	 PROJ=fecreader
	
	 # This is everything to handle the files before the body rows are entered
	 # After the body rows are entered, the exotic ones must be superceded
	
	 source /projects/$NAME/virt/bin/activate
	 /projects/$NAME/src/$NAME/$PROJ/manage.py scrape_rss_filings
	 /projects/$NAME/src/$NAME/$PROJ/manage.py download_new_filings
	 /projects/$NAME/src/$NAME/$PROJ/manage.py enter_headers_from_new_filings
	 /projects/$NAME/src/$NAME/$PROJ/manage.py set_new_filing_details
	 /projects/$NAME/src/$NAME/$PROJ/manage.py mark_amended
	 /projects/$NAME/src/$NAME/$PROJ/manage.py send_body_row_jobs
	 
	 

#### Details:

| Script  | Domain | Flags | Description |
| ------------ | ------------- | ------------ | ---------------- |
| fec_alerts > scrape_rss_filings | Runs on all RSS items | None | Creates new_filing objects from RSS feed |
| formdata > download_new_filings | Runs on all new_filings with filing_is_downloaded=False, header_is_processed=False | Sets filing_is_downloaded to True  | Download files from FTP. Mark them as having been downloaded. |
| enter_headers_from_new_filings  | filing_is_downloaded=True, header_is_processed=False | Sets header_is_processed = True | Enter file headers; don't mark them as either amended or not. Only enters summary data available--for some schedules the total expenditures must be calculated after the body row jobs are entered. |
| fec_alerts > set_new_filing_details  | new_filing_details_set=False,header_is_processed=True | sets new_filing_details_set | Set data fields in the new filing from the parsed Filing_Header; don't handle unsummarized forms, like F24's |
| fec_alerts > mark_amended | previous_amendments_processed=False,new_filing_details_set=True | sets previous_amendments_processed | Mark the originals as being amended (for new_filing objects) |
| formdata > send_body_row_jobs | filing_is_downloaded=True, header_is_processed=True, data_is_processed=False, previous_amendments_processed=True | celery worker sets data_is_processed=True | Queue filing body row entry for execution by celery processes |


---

#### second step 

	20,50 * * * * /projects/realtimefec/bin/load_step_2.sh 2>&1 >> /mnt/cron/load_2.log
  
---
  
	#!/bin/bash
	NAME=realtimefec
	PROJ=fecreader
	
	source /projects/$NAME/virt/bin/activate
	/projects/$NAME/src/$NAME/$PROJ/manage.py mark_superceded_body_rows
	/projects/$NAME/src/$NAME/$PROJ/manage.py update_dirty_committee_times
	/projects/$NAME/src/$NAME/$PROJ/manage.py process_skede_lines


#### Details:



| Script  | Domain | Flags | Description |
| ------------ | ------------- | ------------ | ---------------- |
|  formdata > mark_superceded_body_rows | previous_amendments_processed=True,header_is_processed=True, data_is_processed=True, body_rows_superceded=False | sets body_rows_superceded | Mark the body rows as being superceded as appropriate; also set the new_filing data for stuff that can only be calculated after body rows have run. |
| summary_data > update_dirty_committee_times | Runs where committee_overlay dirty flag is set | unsets dirty flag on committee | Recalculate committee summaries |
| formdata > process_skede_lines | data_is_processed=True, body_rows_superceded=True, ie_rows_processed=False | sets ie_rows_processed  | Set the name and details of the candidate targetted |


#### hourly updates 


	2 * * * * /projects/realtimefec/bin/hourly_updates.sh 2>&1 >> /mnt/cron/hourly.log
---
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
	/projects/$NAME/src/$NAME/$PROJ/manage.py update_committee_os_totals
	/projects/$NAME/src/$NAME/$PROJ/manage.py remove_blacklisted
	

#### Details:



| Script  | Domain | Flags | Description |
| ------------ | ------------- | ------------ | ---------------- |
| summary_data > mark_amended_skede_lines | runs on all filings with skede lines present | None | makes sure all superceded sked e filings are listed as superceded in the body rows |
| summary_data > set_candidate_pac | Summarizes all pacs for ACTIVE_CYCLES | None | recalculates per-candidate outside spending by each outside spender |
| summary_data > make_candidate_os_aggregates | Summarizes for all candidates in ACTIVE_CYCLES | None | recalculates per-candidate outside spending by each outside spender |
| summary_data > update_race_aggregates | CURRENT_CYCLE | None | sets race totals |
| summary_data > update_all_candidate_times | CURRENT_CYCLE | None | recreates candidate_time objects |
| summary_data > update_committee_os_totals | ACTIVE_CYCLES | None | sets pac-wise aggregates | 
| summary_data > remove_blacklisted | all time | None | removes some objects from blacklisted pacs that historically report fictitious amounts 

