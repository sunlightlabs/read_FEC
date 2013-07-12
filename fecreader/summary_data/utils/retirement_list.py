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
{'name':'MARKEY, EDWARD JOHN' , 'fec_id':'H6MA07101', 'seeking_other_office':'Senate'},
{'name':'BRALEY, BRUCE L' , 'fec_id':'H6IA01098', 'seeking_other_office':'Senate'},
{'name':'PETERS, GARY' , 'fec_id':'H8MI09068', 'seeking_other_office':'Senate'}, 
{'name':'SCHWARTZ, ALLYSON Y.' , 'fec_id':'H4PA13124', 'seeking_other_office':'Governor'}, 
{'name':'HANABUSA, COLLEEN WAKAKO' , 'fec_id':'H2HI02110', 'seeking_other_office':'Senate'},
{'name':'PALLONE, FRANK JR' , 'fec_id':'H8NJ03073', 'seeking_other_office':'Senate'}, 
{'name':'HOLT, RUSH D.' , 'fec_id':'H6NJ12144', 'seeking_other_office':'Senate'}, 
{'name':'CAPITO, SHELLEY MOORE MS.' , 'fec_id':'H0WV02138', 'seeking_other_office':'Senate'}, 
{'name':'BROUN, PAUL COLLINS' , 'fec_id':'H8GA10049', 'seeking_other_office':'Senate'}, 
{'name':'CASSIDY, WILLIAM' , 'fec_id':'H8LA00017', 'seeking_other_office':'Senate'}, 
{'name':'GINGREY, PHIL' , 'fec_id':'H2GA11149', 'seeking_other_office':'Senate'}, 
{'name':'KINGSTON, JACK' , 'fec_id':'H2GA01157', 'seeking_other_office':'Senate'}, 
# RETIRING:
{'name':'BACHMANN, MICHELE' , 'fec_id':'H6MN06074'}, 
{'name':'CAMPBELL, JOHN BT III' , 'fec_id':'H6CA48039'}, 
]

## More notes:
# Todd Akin really has filed to run for senate in 2018: http://images.nictusa.com/pdf/750/12021083750/12021083750.pdf - he did it November 7, 2012--the day after he lost
