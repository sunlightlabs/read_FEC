
# hacks to turn term_class into election year and vice versa

def get_election_year_from_term_class(term_class):
    # make sure we've got a string
    term_class = str(term_class)
    if term_class == '1':
        return 2018
    elif term_class == '2':
        return 2014
    elif term_class == '3':
        return 2016
    return None

def get_term_class_from_election_year(election_year):
    #make sure we've got an int
    election_year = int(election_year)
    if election_year in (2018, 2012, 2006, 2000):
        return '1'
    elif election_year in (2014, 2008, 2002):
        return '2'
    elif election_year in (2016, 2010, 2004):
        return '3'
    return None