"""el_internationalisation: bidi support

    A set of functions to aid in improving support for bidirectional text.

    Todo:
        * add DocStrings
        * refactor type hinting for Python 3.10+
"""

import regex

def is_bidi(text):
    """Indicates if string requires bidirectional support.

    Args:
        text (str): string to analyse

    Returns:
        bool: returns True if the string is RTL, returns False otherwise.
    """
    bidi_reg = r'[\p{bc=AL}\p{bc=AN}\p{bc=LRE}\p{bc=RLE}\p{bc=LRO}\p{bc=RLO}\p{bc=PDF}\p{bc=FSI}\p{bc=RLI}\p{bc=LRI}\p{bc=PDI}\p{bc=R}]'
    return bool(regex.search(bidi_reg, text))

isbidi = is_bidi

def bidi_envelope(text, dir = "auto", mode = "isolate"):
    """Wrap string in bidirectional formatting characters.

    Args:
        text (str): String to wrap.
        dir (str, optional): Primary text direction of string: "ltr", "rtl" or "auto". Defaults to auto if mode is "isolate". Defaults to "rtl" if mode is "embedded" or "override".
        mode (str, optional): Bidi formatting to be applied: isolate, embedded, override. Defaults to "isolate"

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
    elif mode == "embedding":
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

def strip_bidi(text):
    """Strip bidi formatting characters.

    Strip bidi formatting characters: U+2066..U+2069, U+202A..U+202E

    Args:
        text (str): String to process.

    Returns:
        str: _description_
    """
    return regex.sub('[\u202a-\u202e\u2066-\u2069]', '', text)
