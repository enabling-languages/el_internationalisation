"""el_internationalisation: analyse characters

    Functions to assist in analysing Unicode strings, and assist in debugging encoding issues.

"""

import unicodedataplus, prettytable, regex
from typing import List, Set, Tuple, Optional
from .bidi import bidi_envelope, is_bidi

def splitString(text: str) -> list:
    """Typecast string to a list, splitting sting into a list of characters.
    Character level tokenisation.

    Args:
        text (str): Unicode string to be tokenised.

    Returns:
        list: a list of single Unicode character tokens.
    """
    return list(text)

def utf8len(text: str) -> int:
    """Number of bytes required when string is using UTF-8 encoding.

    Args:
        text (str): String to be analysed

    Returns:
        int: number of bytes in UTF-8 encoded string.
    """
    return len(text.encode('utf-8'))

def utf16len(text: str) -> int:
    """Number of bytes required when string is using UTF-16 LE or BE encoding.

    Args:
        text (str): String to be analysed

    Returns:
        int: number of bytes in UTF-16 LE or BE encoded string.
    """
    return len(text.encode('utf-16-le'))

def add_dotted_circle(text: str) -> str:
    """Add dotted circle to combining diacritics in a string.

    Args:
        text (str): string to parse

    Returns:
        str: transformed string with combining diacritics in string applied to a dotted circle.
    """
    return "".join(["\u25CC" + i if unicodedataplus.combining(i) else i for i in list(text)])

# codepoints and characters in string
#
# Usage:
#    eli.codepoints("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪")
#    eli.cp("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪", extended=True)
#    eli.cp("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪", prefix=True, extended=True)

def codepoints(text: str, prefix: bool = False, extended: bool = False) -> str:
    """Identifies codepoints in a string.

    Args:
        text (str): string to analyse.
        prefix (bool, optional): flag indicating if the U+ prefix is appended to codepoint. Defaults to False.
        extended (bool, optional): flag indicating if character is displayed after codepoint. Defaults to False.

    Returns:
        str: string of Unicode codepoints in analysed string.
    """
    if extended:
        return ' '.join(f"U+{ord(c):04X} ({c})" for c in text) if prefix else ' '.join(f"{ord(c):04X} ({c})" for c in text)
    else:
        # return ' '.join('U+{:04X}'.format(ord(c)) for c in text) if prefix else ' '.join('{:04X}'.format(ord(c)) for c in text)
        return ' '.join(f"U+{ord(c):04X}" for c in text) if prefix else ' '.join(f"{ord(c):04X}" for c in text)

cp = codepoints

def codepointsToChar(codepoints: str) -> str:
    """Convert a string of comma or space separated unicode codepoints to characters.

    Convert a string of comma or space separated unicode codepoints to characters.
    Codepoints do not have to have the U+ prefix, e.g. "U+0063 U+0301", "U+0063, U+0301",
    "0063 0301", or "0063, 0301" are valid representations of codepoints.
    For this example the string 'ć' is returned.

    Args:
        codepoints (str): A string containing space or comma separated Unicode codepoints.

    Returns:
        str: Unicode characters represented by the codepoints
    """
    codepoints = codepoints.lower().replace("u+", "")
    cplist: List[str] = regex.split(", |,| ", codepoints)
    results: str = ""
    for c in cplist:
        results += chr(int(c, 16))
    return results

def unicode_data(text: str) -> None:
    """Display Unicode data for each character in string.

    Perform a character tokenisation on a string, and generate a table containing 
    data on some Unicode character properties, including character codepoint and name, 
    script character belongs to, 

    Args:
        text (str): string to analyse.
    """
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
    print(t)

udata = unicode_data

def scan_bidi(text: str) -> Tuple[bool, bool, bool, bool, bool, Set[Optional[str]]]:
    """Analyse string for bidi support.

    The script returns a tuple indicating if sting contains bidirectional text and if it uses bidirectional formatting characters. Returns a tuple of:
      * bidi_status - indicates if RTL characters in string,
      * isolates - indicates if bidi isolation formatting characters are in string,
      * embeddings - indicates if bidi embedding formatting characters are in string,
      * marks - indicates if bidi marks are in the string,
      * overrides - indicates if bidi embedding formatting characters are in string,
      * formatting_characters - a set of bidirectional formatting characters in string.
    
    Args:
        text (str): Text to analyse

    Returns:
        Tuple[bool, bool, bool, bool, bool]: Summary of bidi support analysis
    """
    bidi_status: bool = is_bidi(text)
    isolates: bool = bool(regex.search('[\u2066\u2067\u2068]', text)) and bool(regex.search('\u2069', text))
    embeddings: bool = bool(regex.search('[\u202A\u202B]', text)) and bool(regex.search('\u202C', text))
    marks: bool = bool(regex.search('[\u200E\u200F]', text))
    overrides: bool = bool(regex.search('[\u202D\u202E]', text)) and bool(regex.search('\u202C', text))
    #formatting_status: bool = bool(regex.search('[\u202a-\u202e\u2066-\u2069]', text))
    formating_characters: Set[Optional[str]] = set(regex.findall('[\u200e\u200f\u202a-\u202e\u2066-\u2069]', text))
    formating_characters = {f"U+{ord(c):04X} ({unicodedataplus.name(c,'-')})" for c in formating_characters if formating_characters is not None}
    return (bidi_status, isolates, embeddings, marks, overrides, formating_characters)

scan = scan_bidi
