from string import maketrans

# Some windows (?) characters that appear to have gotten in...

pretrans = "\x85\x91\x92\x93\x94\x97"
posttrans = ".''\"\"-"
trans = maketrans(pretrans, posttrans)

# also remove tabs. 
toremove = "\xA5\xA0\x22\x26\x3C\x3E\xA0\xA1\xA2\xA3\xA4\xA5\xA6\xA7\xA8\xA9\xAA\xAB\xAC\xAD\xAE\xAF\xB0\xB1\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xBB\xBC\xBD\xBE\xBF\xD7\xF7\x95\x96\x98\x99\t"

def utf8_clean(raw_string):
    raw_string = raw_string.translate(None, toremove)
    return raw_string.translate(trans)
    
def recode_to_utf8(self, text):
    """ FEC spec allows ascii 9,10,11,13,32-126,128-156,160-168,173; the below seems to work for some weird chars """
    text_uncoded = text.decode('cp1252')
    text_fixed = text_uncoded.encode('utf8')
    return text_fixed
    
    