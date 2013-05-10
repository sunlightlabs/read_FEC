from cStringIO import StringIO


def dict_to_hstore(python_dict):
    """ Assume it's a '1-dimensional' hash--that is, just a list of key values where everything is quoted.
    There's an implementation of this here ( HstoreAdapter ) https://github.com/psycopg/psycopg2/blob/master/lib/extras.py
    but the comments say that it is "painfully inefficient!"
    
    """
    
    hstore = StringIO()
    
    first_row = True
    for key in python_dict:
        if not first_row:
            hstore.write(",")
        else:
            first_row=False
        #dictstring = "\"%s\"=>\"%s\"" % (key, python_dict[key])
        hstore.write("\"%s\"=>\"%s\"" % (key, python_dict[key]))
    #print "\n\n\n\nvalue is: %s" % hstore.getvalue()
    #assert False
    return hstore.getvalue()
    