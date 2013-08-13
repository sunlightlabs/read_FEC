import difflib

def longest_match(text1, text2):
    isjunk=None

    # Case insensitive here--this might not be the right choice
    s = difflib.SequenceMatcher(isjunk,text1.lower(), text2.lower());

    total_match_length = 0

    for opcode, a0, a1, b0, b1 in  s.get_opcodes():
        if opcode == 'equal':
            this_match = s.a[a0:a1]
            this_length = len(this_match)
            total_match_length = total_match_length + this_length

    return total_match_length
    
