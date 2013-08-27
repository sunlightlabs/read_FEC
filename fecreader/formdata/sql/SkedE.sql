
-- SQL to deal with indexes:
-- First drop all the indexes that django creates by default for a primary key:

alter table formdata_skede drop constraint formdata_skede_pkey;

-- We need a way to get rows without a table scan, though, so we're gonna have one index per row on the filing number. 
-- We're cutting down the fillfactor to allow for faster loads, at the expense of more memory, probably
--For more see: http://www.postgresql.org/docs/9.2/static/sql-createindex.html.

create index formdata_skede_fnumber on formdata_skede (filing_number)  WITH (fillfactor = 50);

-- Even though it'll slow our inserts down, we reuse this table as ie data, so index it. 

-- index on candidate id, state, race
-- TODO--THE INDEXES!