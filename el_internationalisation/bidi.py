"""el_internationalisation: bidi support

    A set of functions to aid in improving support for bidirectional text.

    Todo:
        * add DocStrings
        * refactor type hinting for Python 3.10+
"""

import regex as _regex
import arabic_reshaper as _arabic_reshaper
from bidi.algorithm import get_display as _get_display
from pyfribidi import log2vis as _log2vis, RTL as _RTL
from collections import Counter as _Counter
import unicodedataplus as _unicodedataplus

####################
#
# Detect if string contains RTL CHARACTERS
#
####################

def is_bidi(text):
    """Indicates if string requires bidirectional support for RTL characters.

    Tests for characters bith bidirectional category indicating RTL text, or for directional formating control characters.

    Args:
        text (str): string to analyse

    Returns:
        bool: returns True if the string is RTL, returns False otherwise.
    """
    bidi_reg = r'[\p{bc=AL}\p{bc=AN}\p{bc=LRE}\p{bc=RLE}\p{bc=LRO}\p{bc=RLO}\p{bc=PDF}\p{bc=FSI}\p{bc=RLI}\p{bc=LRI}\p{bc=PDI}\p{bc=R}]'
    return bool(_regex.search(bidi_reg, text))

isbidi = is_bidi

####################
#
# Create an explicit embedding level
#
####################

def bidi_envelope(text, dir = "auto", mode = "isolate"):
    """Wrap string in bidirectional formatting characters.

    Args:
        text (str): String to wrap.
        dir (str, optional): Primary text direction of string: "ltr", "rtl" or "auto". Defaults to auto if mode is "isolate". Defaults to "rtl" if mode is "embedded" or "override".
        mode (str, optional): Bidi formatting to be applied: isolate, embed, override. Defaults to "isolate"

    Returns:
        str: initial string wrapped in bidirectional formatting characters.
    """
    mode = mode.lower()
    dir = dir.lower()
    if mode == "isolate":
        if dir == "rtl":
            text = "\u2067" + text + "\u2069"
        elif dir == "ltr":
            text = "\u2066" + text + "\u2069"
        elif dir == "auto":
            text = "\u2068" + text + "\u2069"
    elif mode == "embed":
        if dir == "auto":
            dir = "rtl"
        if dir == "rtl":
            text = "\u202B" + text + "\u202C"
        elif dir == "ltr":
            text = "\u202A" + text + "\u202C"
    elif mode == "override":
        if dir == "auto":
            dir = "rtl"
        if dir == "rtl":
            text = "\u202E" + text + "\u202C"
        elif dir == "ltr":
            text = "\u202D" + text + "\u202C"
    return text

envelope = bidi_envelope

####################
#
# Strip directional formatting control characters
#
####################

def strip_bidi(text):
    """Strip bidi formatting characters.

    Strip bidi formatting characters: U+2066..U+2069, U+202A..U+202E

    Args:
        text (str): String to process.

    Returns:
        str: _description_
    """
    return _regex.sub('[\u202a-\u202e\u2066-\u2069]', '', text)

####################
#
# Render RTL in an environment that doesn't support UBA
#
####################

def rtl_hack(text: str, arabic: bool = True, fribidi: bool = True) -> str:
    """Visually reorders Arabic or Hebrew script Unicode text

    Visually reorders Arabic or Hebrew script Unicode text. For Arabic script text,
    individual Unicode characters are substituting each character for its equivalent
    presentation form. The modules are used to overcome lack of bidirectional algorithm
    and complex font rendering in some modules and terminals.

    It is better to solutions that utilise proper bidirectional algorithm and font
    rendering implementations. For matplotlib use the mplcairo backend instead. For
    annotating images use Pillow. Both make use of libraqm.

    arabic_reshaper module converts Arabic characters to Arabic Presentation Forms:
        pip install arabic-reshaper

    bidi.algorithm module converts a logically ordered string to visually ordered
    equivalent.
        pip install python-bidi

    Args:
        text (str): _description_

    Returns:
        str: _description_
    """
    if fribidi:
        return _log2vis(text, _RTL)
    return _get_display(_arabic_reshaper.reshape(text)) if arabic == True else _get_display(text)

####################
#
# Clean presentation forms
#
#    For Latin and Armenian scripts, use either folding=True or folding=False (default), 
#    while for Arabic and Hebrew scripts, use folding=False.
#
####################

def has_presentation_forms(text):
    pattern = r'([\p{InAlphabetic_Presentation_Forms}\p{InArabic_Presentation_Forms-A}\p{InArabic_Presentation_Forms-B}]+)'
    return bool(_regex.findall(pattern, text))

def clean_presentation_forms(text, folding=False):
    def clean_pf(match, folding):
        return  match.group(1).casefold() if folding else _unicodedataplus.normalize("NFKC", match.group(1))
    pattern = r'([\p{InAlphabetic_Presentation_Forms}\p{InArabic_Presentation_Forms-A}\p{InArabic_Presentation_Forms-B}]+)'
    return _regex.sub(pattern, lambda match, folding=folding: clean_pf(match, folding), text)

def scan_bidi(text):
    """Analyse string for bidi support.

    The script returns a tuple indicating if sting contains bidirectional text and if it uses bidirectional formatting characters. Returns a tuple of:
      * bidi_status - indicates if RTL characters in string,
      * isolates - indicates if bidi isolation formatting characters are in string,
      * embeddings - indicates if bidi embedding formatting characters are in string,
      * marks - indicates if bidi marks are in the string,
      * overrides - indicates if bidi embedding formatting characters are in string,
      * formatting_characters - a set of bidirectional formatting characters in string.
      * presentation_forms - indicates if presentation forms are in the string.

    Args:
        text (str): Text to analyse

    Returns:
        Tuple[bool, bool, bool, bool, bool, Set[Optional[str]], bool]: Summary of bidi support analysis
    """
    bidi_status = is_bidi(text)
    isolates = bool(_regex.search(r'[\u2066\u2067\u2068]', text)) and bool(_regex.search(r'\u2069', text))
    embeddings = bool(_regex.search(r'[\u202A\u202B]', text)) and bool(_regex.search(r'\u202C', text))
    marks = bool(_regex.search(r'[\u200E\u200F]', text))
    overrides = bool(_regex.search(r'[\u202D\u202E]', text)) and bool(_regex.search(r'\u202C', text))
    formating_characters = set(_regex.findall(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]', text))
    formating_characters = {f"U+{ord(c):04X} ({_unicodedataplus.name(c,'-')})" for c in formating_characters if formating_characters is not None}
    presentation_forms = has_presentation_forms(text)
    return (bidi_status, isolates, embeddings, marks, overrides, formating_characters, presentation_forms)

scan = scan_bidi

####################
#
# Strong directionality
#
#    Detect directionality based on either first string character or dominant directionality in string.
#
####################

def first_strong(s):
    properties = ['ltr' if v == "L" else 'rtl' if v in ["AL", "R"] else "-" for v in [_unicodedataplus.bidirectional(c) for c in list(s)]]
    for value in properties:
        if value == "ltr":
            return "ltr"
        elif value == "rtl":
            return "rtl"
    return None

def dominant_strong_direction(s):
    count = _Counter([_unicodedataplus.bidirectional(c) for c in list(s)])
    rtl_count = count['R'] + count['AL'] + count['RLE'] + count["RLI"]
    ltr_count = count['L'] + count['LRE'] + count["LRI"] 
    return "rtl" if rtl_count > ltr_count else "ltr"
