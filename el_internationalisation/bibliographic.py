import regex
import html
from .ustrings import normalise, codepoints
from lxml import etree
from typing import Union
import unicodedataplus
import icu

# Languages to normalise : ISO-639-1 and ISO-639-2/B language codes.
thai_lao_rom_languages = ["lao", "lo", "tha", "th"]
cyrillic_rom_languages = ["be", "bel", "sla", "bg", "bul", "chu", "cu", "mk", "mac", "ru", "rus", "rue", "uz", "uzb"]

##############################
#
# Normalisation of Thai and Lao romanisations.
#
##############################
# Default value:
# THAI_LAO_ROM: str = None
# def set_THAI_LAO_ROM(value: Union[str, None] = None) -> Union[str, None]:
#     """Set value of THAI_LAO_ROM to 1997 or 2011.
# 
#     Changes in the 2011 Thai and Lao romanisation tables leds to 
#     differing interpretations of which characters to use for certain
#     romanisations.
# 
#     1997 uses U+031C (based on MARC-8 mapping)
#     2011 uses U+0328 (based on glph in tables)
# 
#     Args:
#         value (str): returns normalised string.
# 
#     Returns:
#         None.
#     """
#     if value in [1997, 2011]:
#         return value
#     return None

# Normalise Thai and Lao romanisations
def clean_thai_lao_rom(item: str, mode: str):
    return item.replace("\u031C", "\u0328") if mode == 2011 else item.replace("\u0328", "\u031C")

##############################
#
# Normalisation of Cyrillic romanisations.
#
##############################
# Default value:
# CYRILLIC_ROM: bool = False
# def set_CYRILLIC_ROM(value: bool = False) -> bool:
#     """Normalise Cyrillic romanisations.
# 
#     Convert romanisaed Cyrillic strings using the half forms 
#     U+FE20 and U+FE21 to U+0361.
# 
#     Args:
#         value (bool): Indicates if Cyrillic normalisation required. 
#                       For True, normalise Cyrillic strings. For False, 
#                       do not normalise Cyrillic strings.
# 
#     Returns:
#         bool: 
#     """
#     if value in [True, False]:
#         return value
#     return False

def clean_cyrillic_rom(item: str) -> str:
    """Normalise Cyrillic romanisations.

    Convert romanisaed Cyrillic strings using the half forms 
    U+FE20 and U+FE21 to U+0361.

    Args:
        item (str): String to normalise

    Returns:
        str: Normalised string
    """
    item - regex.sub(r'([tT])\uFE20([sS])\uFE21\u0307', r'\1\u0361\u034F\u0307\2', item)
    item = regex.sub(r'([tT])\uFE20\u0307([sS])\uFE21', r'\1\u0361\u034F\u0307\2', item)
    item = regex.sub(r'([oO])\u0304\uFE20([tT])\uFE21', r'\1\u0304\u0361\2', item)
    item = regex.sub(r'([iI])\uFE20([eEoO])\u0328\uFE21', r'\1\u0361\2\u0328', item)
    item = regex.sub(r'([dD])\uFE20([zZ])\u030C\uFE21', r'\1\u0361\1\u030C', item)
    item = regex.sub(r'([dDiIkKpnNPtTzZ])\uFE20([aAeEhHgGnNoOsSuUzZ])\uFE21', r'\1\u0361\2', item)
    return item

##############################
#
# Clean bibliographic data.
#
##############################

def clean_marc_subfield(item: str, lang: str, norm_form: str = "NFD", thai_lao_rom: Union[str, None] = None, cyrillic_rom: bool = False ) -> str:
    """_summary_

    Args:
        item (str): _description_
        lang (str): _description_
        norm_form (str, optional): _description_. Defaults to "NFD".

    Returns:
        str: _description_
    """
    item = normalise("NFD", html.unescape(item), use_icu=True)
    norm_form = norm_form.upper()
    if lang in thai_lao_rom_languages:
        if thai_lao_rom:
            item = clean_thai_lao_rom(item, thai_lao_rom)
    if lang in cyrillic_rom_languages:
        if cyrillic_rom:
            item = clean_cyrillic_rom(item)
    item = normalise(norm_form, item, use_icu=True) if norm_form != "NFD" else item
    return item

##############################
#
# Repair Voyager SMP characters.
#
##############################
#
#    Assumes HTML/XML hexadecimal NCRs
#    as used in MARC-8 records

REPAIRABLE_SCRIPTS = ["adlm", "bamu", "bass", "hmng", "mend", "palm", "rohg", "xsux", "yezi"]

def repair_smp(text: str, script: str) -> str:
    """Repair SMP characters in MARC-8 encoded records exported from Voyager LMS

    Supported scripts:
        adlm: Adlam - U+1E900–U+1E95F
        bamu: Bamum - U+A6A0–U+A6FF, U+16800–U+16A3F   ??
        bass: Bassa Vah - U+16AD0-U+16AFF              ??
        hmng: Pahawh Hmong - U+16B00-U+16B8F           ??
        mend: Mende - U+1E800-1E8DF                    ??
        palm: Palmyrene - U+10860-U+1087F              ??
        rohg: Rohingya - U+10D00–U+10D3F
        xsux: Cuneiform - U+12000-U+123FF, U+12400-U+1247F, U+12480–U+1254F
        yezi: Yezidi - U+10E8D-U+10EBF                 ??

    Unsupported:
        shaw: Shavian - Voyager converts Shavian characters to U+FFFD (Replacement Character)

    Args:
        text (str): Subfield value to be repaired
        script (str): Writing system (script)

    Returns:
        str: Repaired subfield value, if it can be repaired, else original subfield value.
    """
    repair_data = {
        "adlm": (r'&#x[eE]9[0-5][0-9a-fA-F];', r'&#x[eE]9', r'&#x1e9'),
        "bamu": (r'&#x6[8-9Aa][0-9A-Fa-f][0-9A-Fa-f];', r'&#x6', r'&#x16'),
        "bass": (r'&#x6[aA][D-Fd-f][0-9A-Fa-f];', r'&#x6a', r'&#x16a'),
        "hmng": (r'&#x6[bB][0-8][0-9A-Fa-f];', r'&#x6[bB]' r'&#x16b'),
        "mend": (r'&#x[eE]8[0-9A-Da-d][0-9A-Fa-f];', r'&#x[eE]8', r'&#x1e8'),
        "palm": (r'&#x08[6-7][0-9A-Fa-f];', r'&#x08', r'&#x108'),
        "rohg": (r'&#x0[dD][0-3][0-9a-fA-F];', r'&#x0[dD]', r'&#x10d'),
        "xsux": (r'&#x2[0-5][0-9a-fA-F][0-9a-fA-F];', r'&#x2', r'&#x12'),
        "yezi": (r'&#x0[eE][8-9A-Ba-b][0-9A-Fa-f];', r'&#x0[eE]', r'&#x10e')
    }
    try:
        if regex.match(repair_data[script][0], text):
            return regex.sub(repair_data[script][1], repair_data[script][2], text)
        else:
            return text
    except KeyError:
        return text

##############################
#
# XML-XSLT Transformation
#
##############################
#
#    xmlfile is either a XML file or a BytesIO stream of XML. See intl_bib_clean.py.
#

def xsl_transformation(xslfile, xmlfile = None, xmlstring = None, params={}):
    xslt_tree = etree.parse(xslfile)
    transform = etree.XSLT(xslt_tree)
    xml_contents = xmlstring
    if not xml_contents:
        if xmlfile:
            xml_contents = etree.parse(xmlfile)
    result = transform(xml_contents, **params)
    return result

##############################
#
# Anomoly detection
#
##############################
#
#
#
problem_chars_pattern = regex.compile(r'[\p{Bidi_Control}\p{Cs}\p{Co}\p{Cn}\u0333\u3013\uFFFD]')
# problem_chars_pattern = regex.compile(r'[\p{Cf}\p{Cs}\p{Co}\p{Cn}\u0333\u3013\uFFFD]')
problem_chars = ['\u0333', '\u3013', '\uFFFD']
problem_chars.extend(list(icu.UnicodeSet(r'\p{Bidi_Control}')))
# problem_chars.extend(list(icu.UnicodeSet(r'\p{Cf}')))
problem_chars.extend(list(icu.UnicodeSet(r'\p{Cs}')))
problem_chars.extend(list(icu.UnicodeSet(r'\p{Co}')))
problem_chars.extend(list(icu.UnicodeSet(r'\p{Cn}')))

def detect_anomalies(text: str) -> set[str]:
    problematic = set()
    if regex.search(problem_chars_pattern, text):
        for char in problem_chars:
            if char in text:
                problematic.add(f"{codepoints(char)} ({unicodedataplus.name(char)})")
    return problematic

def register_anomalies(sub_field: str):
    check = detect_anomalies(sub_field)
    if check:
        print(*sorted(check), sep="\n", end="\n\n")
    return None