import unicodedataplus


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
#    elu.codepoints("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪")
#    elu.cp("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪", extended=False)
#    elu.cp("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪", prefix=False, extended=False)

def codepoints(text, prefix=True, extended=True):
    if extended:
        return ' '.join(f"U+{ord(c):04X} ({c})" for c in text) if prefix else ' '.join(f"{ord(c):04X} ({c})" for c in text)
    else:
        return ' '.join('U+{:04X}'.format(ord(c)) for c in text) if prefix else ' '.join('{:04X}'.format(ord(c)) for c in text)

cp = codepoints





# Prepend dotted circle to combining diacritics in a string
# Input string, returns string
def add_dotted_circle(text):
    return "".join(["\u25CC" + i if unicodedataplus.combining(i) else i for i in list(text)])