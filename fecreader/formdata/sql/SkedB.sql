
-- SQL to deal with indexes:
-- First drop all the indexes that django creates by default for a primary key:

alter table formdata_skedb drop constraint formdata_skedb_pkey;

-- We need a way to get rows without a table scan, though, so we're gonna have one index per row on the filing number. 
-- We're cutting down the fillfactor to allow for faster loads, at the expense of more memory, probably
--For more see: http://www.postgresql.org/docs/9.2/static/sql-createindex.html.

create index formdata_skedb_fnumber on formdata_skedb (filing_number)  WITH (fillfactor = 50);
