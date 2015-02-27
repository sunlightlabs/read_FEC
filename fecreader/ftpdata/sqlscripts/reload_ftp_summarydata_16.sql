-- Procedure to empty and reload summary data; 
\set cycle 16
\set year 2016
\set datadir /projects/realtimefec/src/realtimefec/fecreader/ftpdata/data

-- Insane variable concatenization scheme. Oy. 
\set committeefile '\'' :datadir '/' :cycle '/cm' :cycle '-fixed.txt\''
\set candidatefile '\'' :datadir '/' :cycle '/cn' :cycle '-fixed.txt\''
\set cclfile '\'' :datadir '/' :cycle '/ccl' :cycle '-fixed.txt\''

-- delete all records
delete from ftpdata_candidate where cycle = :year;
delete from ftpdata_committee where cycle = :year;
delete from ftpdata_candcomlink where cycle = :year;

-- repopulate

copy ftpdata_committee (cycle, cmte_id, cmte_name, tres_nm, cmte_st1, cmte_st2, cmte_city, cmte_st, cmte_zip, cmte_dsgn, cmte_tp, cmte_pty_affiliation, cmte_filing_freq, org_tp, connected_org_nm, cand_id) from :committeefile with delimiter as '|' null as '';

copy ftpdata_candidate (cycle, cand_id, cand_name, cand_pty_affiliation, cand_election_year, cand_office_st, cand_office, cand_office_district, cand_ici, cand_status, cand_pcc, cand_st1, cand_st2, cand_city, cand_st, cand_zip) from :candidatefile with delimiter as '|' null as '';

copy ftpdata_candcomlink (cycle, cand_id, cand_election_yr, fec_election_yr, cmte_id, cmte_tp, cmte_dsgn, linkage_id) from :cclfile with delimiter as '|';
