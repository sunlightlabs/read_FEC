-- remake the superpac donors table. A hack. 

DROP TABLE IF EXISTS superpac_donors;
 
SELECT fec_alerts_new_filing.committee_name as committee_name, fec_alerts_new_filing.filing_number as filing_number, fec_alerts_new_filing.form_type as form_type, formdata_skeda.form_type as line_type, superceded_by_amendment as superseded_by_amendment, filer_committee_id_number, transaction_id, back_reference_tran_id_number, back_reference_sched_name, entity_type, contributor_name, contributor_organization_name, contributor_last_name, contributor_first_name, contributor_middle_name, contributor_prefix, contributor_suffix, contributor_street_1, contributor_street_2, contributor_city, contributor_state, contributor_zip, election_code, election_other_description, contribution_date, contribution_date_formatted, contribution_amount, contribution_aggregate, contribution_purpose_code, contribution_purpose_descrip, contributor_employer, contributor_occupation, donor_committee_fec_id, donor_committee_name, donor_candidate_fec_id, donor_candidate_name, donor_candidate_last_name, donor_candidate_first_name, donor_candidate_middle_name, donor_candidate_prefix, donor_candidate_suffix, donor_candidate_office, donor_candidate_state, donor_candidate_district, conduit_name, conduit_street1, conduit_street2, conduit_city, conduit_state, conduit_zip, memo_code, memo_text_description, reference_code 
 INTO superpac_donors
 FROM formdata_skeda left join fec_alerts_new_filing on formdata_skeda.filing_number = fec_alerts_new_filing.filing_number  
 WHERE (memo_code isnull or not memo_code = 'X') and committee_type in ('O', 'U') and superceded_by_amendment=False and contribution_amount >= 10000 and contribution_date_formatted >= date('20130101') and is_superceded=False;
 
 alter table superpac_donors add column political_orientation char(1);
 alter table superpac_donors add column designation char(1);
 alter table superpac_donors add column ctype char(1);
 
         
update superpac_donors set political_orientation = (select political_orientation from summary_data_committee_overlay where superpac_donors.filer_committee_id_number = summary_data_committee_overlay.fec_id and summary_data_committee_overlay.cycle = '2014');        
        
update superpac_donors set designation = (select designation from summary_data_committee_overlay where superpac_donors.filer_committee_id_number = summary_data_committee_overlay.fec_id and summary_data_committee_overlay.cycle = '2014');

update superpac_donors set ctype = (select ctype from summary_data_committee_overlay where superpac_donors.filer_committee_id_number = summary_data_committee_overlay.fec_id and summary_data_committee_overlay.cycle = '2014');