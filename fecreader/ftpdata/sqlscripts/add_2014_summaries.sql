set client_encoding = 'latin1';

copy ftpdata_candcomlink (cycle, cand_id, cand_election_yr, fec_election_yr, cmte_id, cmte_tp, cmte_dsgn, linkage_id) from '/Users/jfenton/github-whitelabel/read_FEC/fecreader/ftpdata/data/14/ccl14-fixed.txt' with delimiter as '|';

copy ftpdata_committee (cycle, cmte_id, cmte_name, tres_nm, cmte_st1, cmte_st2, cmte_city, cmte_st, cmte_zip, cmte_dsgn, cmte_tp, cmte_pty_affiliation, cmte_filing_freq, org_tp, connected_org_nm, cand_id) from '/Users/jfenton/github-whitelabel/read_FEC/fecreader/ftpdata/data/14/cm14-fixed.txt' with delimiter as '|' null as '';

copy ftpdata_candidate (cycle, cand_id, cand_name, cand_pty_affiliation, cand_election_year, cand_office_st, cand_office, cand_office_district, cand_ici, cand_status, cand_pcc, cand_st1, cand_st2, cand_city, cand_st, cand_zip) from '/Users/jfenton/github-whitelabel/read_FEC/fecreader/ftpdata/data/14/cn14-fixed.txt' with delimiter as '|' null as '';