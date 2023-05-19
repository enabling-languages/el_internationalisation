import regex
import html
from .ustrings import normalise

# Languages to normalise : ISO-639-1 and ISO-639-2/B language codes.
thai_lao_rom_languages = ["lao", "lo", "tha", "th"]
cyrillic_rom_languages = ["be", "bel", "sla", "bg", "bul", "chu", "cu", "mk", "mac", "ru", "rus", "rue", "uz", "uzb"]

##############################
#
# Normalisation of Thai and Lao romanisations.
#
##############################
THAI_LAO_ROM: str = None
def set_THAI_LAO_ROM(value: str) -> None:
    """Set value of THAI_LAO_ROM to 1997 or 2011.

    Changes in the 2011 Thai and Lao romanisation tables leds to 
    differing interpretations of which characters to use for certain
    romanisations.

    1997 uses U+031C (based on MARC-8 mapping)
    2011 uses U+0328 (based on glph in tables)

    Args:
        value (str): returns normalised string.

    Returns:
        None.
    """
    if value in [1997, 2011]:
        THAI_LAO_ROM = value
    return None

# Normalise Thai and Lao romanisations
def clean_thai_lao_rom(item: str, mode: str):
    return item.replace("\u031C", "\u0328") if mode == 2011 else item.replace("\u0328", "\u031C")

##############################
#
# Normalisation of Cyrillic romanisations.
#
##############################
CYRILLIC_ROM: bool = False
def set_CYRILLIC_ROM(value: bool) -> None:
    """Normalise Cyrillic romanisations.

    Convert romanisaed Cyrillic strings using the half forms 
    U+FE20 and U+FE21 to U+0361.

    Args:
        value (bool): Indicates if Cyrillic normalisation required. 
                      For True, normalise Cyrillic strings. For False, 
                      do not normalise Cyrillic strings.

    Returns:
        None
    """
    CYRILLIC_ROM = value
    return None

def clean_cyrillic_rom(item: str) -> str:
    """Normalise Cyrillic romanisations.

    Convert romanisaed Cyrillic strings using the half forms 
    U+FE20 and U+FE21 to U+0361.

    Args:
        item (str): String to normalise

    Returns:
        str: Normalised string
    """
    item - regex.sub(r'[tT]\uFE20[sS]\uFE21\u0307', r'\1\u0361\u034F\u0307\2', item)
    item = regex.sub(r'[tT]\uFE20\u0307[sS]\uFE21', r'\1\u0361\u034F\u0307\2', item)
    item = regex.sub(r'([oO]\u0304)\uFE20([tT])\uFE21', r'\1\u0304\u0361\2', item)
    item = regex.sub(r'([iI])\uFE20([eEoO]\u0328)\uFE21', r'\1\u0361\2\u0328', item)
    item = regex.sub(r'([dD])\uFE20{[zZ]\u030C)\uFE21', r'\1\u0361$1\u030C', item)
    item = regex.sub(r'([dDiIkKpnNPtTzZ])\uFE20([aAeEhHgGnNoOsSuUzZ])\uFE21', r'\1\u0361\2', item)
    return item

##############################
#
# Clean bibliographic data.
#
##############################

def clean_marc_subfield(item: str, lang: str, norm_form: str = "NFD") -> str:
    """_summary_

    Args:
        item (str): _description_
        lang (str): _description_
        norm_form (str, optional): _description_. Defaults to "NFD".

    Returns:
        str: _description_
    """
    item = normalise("NFD", html.unescape(item))
    norm_form = norm_form.upper()
    if lang in thai_lao_rom_languages:
        if THAI_LAO_ROM:
            item = clean_thai_lao_rom(item, THAI_LAO_ROM)
    if lang in cyrillic_rom_languages:
        if CYRILLIC_ROM:
            item = clean_cyrillic_rom(item)
    item = normalise(norm_form, item) if norm_form != "NFD" else item
    return item
