import unicodedataplus, prettytable, regex
from bidi_support import bidi_envelope, is_bidi

# Typecast string to a list, splitting characters
def splitString(text):
    return list(text)

def utf8len(text):
    return len(text.encode('utf-8'))

def utf16len(text):
    return len(text.encode('utf-16-le'))

# codepoints and characters in string
#
# Usage:
#    eli.codepoints("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪")
#    eli.cp("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪", extended=False)
#    eli.cp("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪", prefix=False, extended=False)

def codepoints(text, prefix=True, extended=True):
    if extended:
        return ' '.join(f"U+{ord(c):04X} ({c})" for c in text) if prefix else ' '.join(f"{ord(c):04X} ({c})" for c in text)
    else:
        return ' '.join('U+{:04X}'.format(ord(c)) for c in text) if prefix else ' '.join('{:04X}'.format(ord(c)) for c in text)

cp = codepoints

# Convert a string of comma or space separated unicode codepoints to characters
#    Usage: codepointsToChar("U+0063 U+0301")
#        or codepointsToChar("0063 0301")
def codepointsToChar(str):
    str = str.lower().replace("u+", "")
    l = regex.split(", |,| ", str)
    r = ""
    for c in l:
        r += chr(int(c, 16))
    return r

# Prepend dotted circle to combining diacritics in a string
# Input string, returns string
def add_dotted_circle(text):
    return "".join(["\u25CC" + i if unicodedataplus.combining(i) else i for i in list(text)])

def unicode_data(text):
    print(f"String: {text}")
    t = prettytable.PrettyTable(["char", "cp", "name", "script", "block", "cat", "bidi", "cc"])
    for c in list(text):
        if unicodedataplus.name(c,'-')!='-':
            cr = bidi_envelope(c, dir="auto", mode="isolate") if is_bidi(c) else c
            t.add_row([cr, "%04X"%(ord(c)), 
                unicodedataplus.name(c,'-'), 
                unicodedataplus.script(c), 
                unicodedataplus.block(c), 
                unicodedataplus.category(c), 
                unicodedataplus.bidirectional(c),
                unicodedataplus.combining(c)])
    return t

udata = unicode_data