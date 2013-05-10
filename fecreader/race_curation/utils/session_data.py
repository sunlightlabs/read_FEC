from datetime import date
# list of retiring senators / house members

# see house press gallery's casualty list http://housepressgallery.house.gov/member-data/casualty-list

# this doesn't include people who've already stepped down / died before 5/1/2013: Inouye, Kerry, Demint

senate_casualties_2014 = [
{'name':'HARKIN, THOMAS RICHARD', 'fec_id':'S4IA00020'},
{'name':'BAUCUS, MAX' , 'fec_id':'S8MT00010'},
{'name':'JOHNSON, TIM' , 'fec_id':'S6SD00051'},
{'name':'CHAMBLISS, C SAXBY' , 'fec_id':'S2GA00118'},
{'name':'ROCKEFELLER, JOHN DAVISON IV' , 'fec_id':'S4WV00027'},
{'name':'JOHANNS, MICHAEL O' , 'fec_id':'S8NE00117'},
{'name':'LEVIN, CARL' , 'fec_id':'S8MI00158'},
{'name':'LAUTENBERG, FRANK R' , 'fec_id':'S2NJ00080'},
]

# some senators who are long departed are still present--use this to exclude them so they don't show up as challengers
senate_exclusions_2014 = [
{'name':'STEVENS, TED', 'fec_id':'S2AK00010'},
{'name':'BROWN, SCOTT P', 'fec_id':'S0MA00109'}
]



# not sure how we're gonna handle this 
house_casualties_2014 = [
{'name':'MARKEY, EDWARD JOHN' , 'fec_id':'H6MA07101'},
]

## More notes:
# Todd Akin really has filed to run for senate in 2018: http://images.nictusa.com/pdf/750/12021083750/12021083750.pdf - he did it November 7, 2012--the day after he lost




# http://www.fec.gov/info/report_dates_2013.shtml
senate_special_elections = [
#{'state':'', 'term_class':'','election_year':'', 'election_code':''},
{'state':'MA', 'term_class':'2','election_year':'2013', 'election_code':'SP', 'election_date':date(2013,4,30), 'cycle':'2014','primary_party':'D'},
{'state':'MA', 'term_class':'2','election_year':'2013', 'election_code':'SP', 'election_date':date(2013,4,30), 'cycle':'2014','primary_party':'R'},
{'state':'MA', 'term_class':'2','election_year':'2013', 'election_code':'SG', 'election_date':date(2013,6,25), 'cycle':'2014'}
]

house_special_elections = [
#{'state':'', 'office_district':'','election_year':'', 'election_code':''},
{'state':'SC', 'office_district':'01','election_year':'2013', 'election_code':'SP', 'election_date':date(2013,3,19), 'primary_party':'D'},
{'state':'SC', 'office_district':'01','election_year':'2013', 'election_code':'SP', 'election_date':date(2013,3,19), 'primary_party':'R'},
{'state':'SC', 'office_district':'01','election_year':'2013', 'election_code':'SR', 'election_date':date(2013,4,2), 'primary_party':'R'},
{'state':'SC', 'office_district':'01','election_year':'2013', 'election_code':'SG', 'election_date':date(2013,5,7)},
{'state':'MO', 'office_district':'08','election_year':'2013', 'election_code':'SG', 'election_date':date(2013,6,4)},
{'state':'IL', 'office_district':'02','election_year':'2013', 'election_code':'SP', 'election_date':date(2013,2,26), 'primary_party':'R'},
{'state':'IL', 'office_district':'02','election_year':'2013', 'election_code':'SP', 'election_date':date(2013,2,26), 'primary_party':'D'},
{'state':'IL', 'office_district':'02','election_year':'2013', 'election_code':'SG', 'election_date':date(2013,4,9)},
]


