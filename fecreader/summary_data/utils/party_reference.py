

# DFL is democratic farmer labor but is really just dem. 
def get_party_from_pty(pty):
    if not pty:
        return None
    pty = pty.upper().strip()
    if pty == 'DEM':
        return 'D'
    elif pty == 'REP':
        return 'R'
    elif pty == 'DFL':
        return 'D'
    return None
    
def get_party_from_term_party(pty):
    if not pty:
        return None
    pty = pty.upper().strip()
    if pty == 'DEMOCRAT':
        return 'D'
    elif pty == 'REPUBLICAN':
        return 'R'
    elif pty == 'INDEPENDENT':
        return 'I'
    return None