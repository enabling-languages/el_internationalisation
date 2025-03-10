####################
#
# el_digits.py
# Convert digits
#   © Enabling Languages 2022
#   Released under the MIT License.
#
####################

import unicodedataplus as _unicodedataplus, regex as _regex
import locale as _locale, icu as _icu

# TODO:
#   * add type hinting
#   * add DocStrings

#
# To Western Arabic digits
#
def convert_digits(text, sep = (",", "."), use_icu=False):
    """Convert formatted number, including native digits, to Western Arabic digits.

    Args:
        text (str): Formatted number as string.
        sep (Tuple[str, str], optional): _description_. Defaults to (",", ".").
        use_icu (bool): Use ICU for number conversion if True. Defaults to False.

    Returns:
        Union[int, float, None]: integer or float equivalent of the string representation of th input number
    """
    nd = _regex.compile(r'^-?\p{Nd}[,.\u066B\u066C\u0020\u2009\u202F\p{Nd}]*$')
    tsep, dsep = sep
    if nd.match(text):
        text = text.replace(tsep, "")
        if use_icu:
            text = ''.join([str(_icu.Char().digit(c)) if c.isdigit() else c  for c in text])
        else:
            text = ''.join([str(_unicodedataplus.decimal(c, c)) for c in text])
        if dsep in text:
            return float(text.replace(dsep, ".")) if dsep != "." else float(text)
        return int(text)
    return None

def is_number(v, sep = (",", ".")):
    nd = _regex.compile(r'^-?\p{Nd}[,.\u066B\u066C\u0020\u2009\u202F\p{Nd}]+$')
    v = "".join(v.split())
    if isinstance(v, int) or isinstance(v, float):
        return isinstance(v, (int, str)), type(v), v
    elif isinstance(v.strip(), str) and nd.match(v.strip()):
        v = convert_digits(v.strip(), sep)
        return True, type(v), v
    else:
        return False, type(v), v

# type[Union[int, float, str]]
#
# convert_numeral_systems()
#
#    Convert numerals between numeral systems
#    Default settings convert python int or float to the specified numeral system.
#    Returns a string
#    Modifications added to assist in changing matplotlib and plotly tick labels: p and scale parameters.
#       These two parameters should be ignored in all other cases.

# import locale as _locale
def convert_numeral_systems(n, p=None, system_out="", system_in="latn", decimal=2, sep_in=["", "."], sep_out=["", "."], scale=None):
    _locale.setlocale(_locale.LC_ALL, "en_US.UTF-8")
    decimal_places = decimal
    if system_in == "latn" and sep_in == ["", "."]:
        n = n / scale if scale else n
        format_string = '%0.' + str(decimal_places) + 'f' if type(n) == float else '%d'
        n = _locale.format_string(format_string, n, grouping=True, monetary=True)
        n = n.replace(",", "ṯ").replace(".", "ḏ")
        #n = str(n)
    if sep_in[0] in [" ", ",", "٬", "\u2009", "\u202F"]:
        n = n.replace(r'[\u0020,٬\u2009\u202F]', "ṯ")
    elif sep_in[0] == ".":
        n = n.replace(".", "ṯ")
    if sep_in[1] in [",", ".", "٫"]:
        n = n.replace(r'[,.٫]', "ḏ")
    data = {
        "adlm" : {'name' : 'Adlam Digits (adlm)', "digits" : "𞥐𞥑𞥒𞥓𞥔𞥕𞥖𞥗𞥘𞥙", "sep_out": [",", "."]},
        "ahom" : {'name' : 'Ahom Digits (ahom)', "digits" : "𑜰𑜱𑜲𑜳𑜴𑜵𑜶𑜷𑜸𑜹"},
        "arab" : {'name' : 'Arabic-Indic Digits (arab)', "digits" : "٠١٢٣٤٥٦٧٨٩"},
        "arabext" : {'name' : 'Extended Arabic-Indic Digits (arabext)', "digits" : "۰۱۲۳۴۵۶۷۸۹", "sep_out_out": ["\u066C", "\u066B"]},
        "bali" : {'name' : 'Balinese Digits (bali)', "digits" : "᭐᭑᭒᭓᭔᭕᭖᭗᭘᭙"},
        "beng" : {'name' : 'Bangla Digits (beng)', "digits" : "০১২৩৪৫৬৭৮৯"},
        "bhks" : {'name' : 'Bhaiksuki  Digits (bhks)', "digits" : "𑱐𑱑𑱒𑱓𑱔𑱕𑱖𑱗𑱘𑱙"},
        "brah" : {'name' : 'Brahmi Digits (brah)', "digits" : "𑁦𑁧𑁨𑁩𑁪𑁫𑁬𑁭𑁮𑁯"},
        "cakm" : {'name' : 'Chakma Digits (cakm)', "digits" : "𑄶𑄷𑄸𑄹𑄺𑄻𑄼𑄽𑄾𑄿"},
        "cham" : {'name' : 'Cham Digits (cham)', "digits" : "꩐꩑꩒꩓꩔꩕꩖꩗꩘꩙"},
        "deva" : {'name' : 'Devanagari Digits (deva)', "digits" : "०१२३४५६७८९"},
        "diak" : {'name' : 'Dhives/Divehi Digits (diak)', "digits" : "𑥐𑥑𑥒𑥓𑥔𑥕𑥖𑥗𑥘𑥙"},
        "fullwide" : {'name' : 'Full-Width Digits (fullwide)', "digits" : "０１２３４５６７８９"},
        "gong" : {'name' : 'Gunjala Gondi digits (gong)', "digits" : "𑶠𑶡𑶢𑶣𑶤𑶥𑶦𑶧𑶨𑶩"},
        "gonm" : {'name' : 'Masaram Gondi digits (gonm)', "digits" : "𑵐𑵑𑵒𑵓𑵔𑵕𑵖𑵗𑵘𑵙"},
        "gujr" : {'name' : 'Gujarati Digits (gujr)', "digits" : "૦૧૨૩૪૫૬૭૮૯"},
        "guru" : {'name' : 'Gurmukhi Digits (guru)', "digits" : "੦੧੨੩੪੫੬੭੮੯"},
        "hmng" : {'name' : 'Pahawh Hmong Digits (hmng)', "digits" : "𖭐𖭑𖭒𖭓𖭔𖭕𖭖𖭗𖭘𖭙"},
        "hmnp" : {'name' : 'Nyiakeng Puachue Hmong Digits (hmnp)', "digits" : "𞅀𞅁𞅂𞅃𞅄𞅅𞅆𞅇𞅈𞅉"},
        "java" : {'name' : 'Javanese Digits (java)', "digits" : "꧐꧑꧒꧓꧔꧕꧖꧗꧘꧙"},
        "kali" : {'name' : 'Kayah Li Digits (kali)', "digits" : "꤀꤁꤂꤃꤄꤅꤆꤇꤈꤉"},
        "khmr" : {'name' : 'Khmer Digits (khmr)', "digits" : "០១២៣៤៥៦៧៨៩"},
        "knda" : {'name' : 'Kannada Digits (knda)', "digits" : "೦೧೨೩೪೫೬೭೮೯"},
        "lana" : {'name' : 'Tai Tham Hora Digits (lana)', "digits" : "᪀᪁᪂᪃᪄᪅᪆᪇᪈᪉"},
        "lanatham" : {'name' : 'Tai Tham Tham Digits (lanatham)', "digits" : "᪐᪑᪒᪓᪔᪕᪖᪗᪘᪙"},
        "laoo" : {'name' : 'Lao Digits (laoo)', "digits" : "໐໑໒໓໔໕໖໗໘໙"},
        "latn" : {'name' : 'Latin Digits (latn)', "digits" : "0123456789"},
        "lepc" : {'name' : 'Lepcha Digits (lepc)', "digits" : "᱀᱁᱂᱃᱄᱅᱆᱇᱈᱉"},
        "limb" : {'name' : 'Limbu Digits (limb)', "digits" : "᥆᥇᥈᥉᥊᥋᥌᥍᥎᥏"},
        "mlym" : {'name' : 'Malayalam Digits (mlym)', "digits" : "൦൧൨൩൪൫൬൭൮൯"},
        "modi" : {'name' : 'Modi Digits (modi)', "digits" : "𑙐𑙑𑙒𑙓𑙔𑙕𑙖𑙗𑙘𑙙"},
        "mong" : {'name' : 'Mongolian Digits (mong)', "digits" : "᠐᠑᠒᠓᠔᠕᠖᠗᠘᠙"},
        "mroo" : {'name' : 'Mro Digits (mroo)', "digits" : "𖩠𖩡𖩢𖩣𖩤𖩥𖩦𖩧𖩨𖩩"},
        "mtei" : {'name' : 'Meetei Mayek Digits (mtei)', "digits" : "꯰꯱꯲꯳꯴꯵꯶꯷꯸꯹"},
        "mymr" : {'name' : 'Myanmar Digits (mymr)', "digits" : "၀၁၂၃၄၅၆၇၈၉", "sep_out": [",", "."]},
        "mymrshan" : {'name' : 'Myanmar Shan Digits (mymrshan)', "digits" : "႐႑႒႓႔႕႖႗႘႙", "sep_out": [",", "."]},
        "mymrtlng" : {'name' : 'Myanmar Tai Laing Digits (mymrtlng)', "digits" : "꧰꧱꧲꧳꧴꧵꧶꧷꧸꧹"},
        "newa" : {'name' : 'Pracalit Digits (newa)', "digits" : "𑑐𑑑𑑒𑑓𑑔𑑕𑑖𑑗𑑘𑑙"},
        "nkoo" : {'name' : "N’Ko Digits (nkoo)", "digits" : "߀߁߂߃߄߅߆߇߈߉"},
        "olck" : {'name' : 'Ol Chiki Digits (olck)', "digits" : "᱐᱑᱒᱓᱔᱕᱖᱗᱘᱙"},
        "orya" : {'name' : 'Odia Digits (orya)', "digits" : "୦୧୨୩୪୫୬୭୮୯"},
        "osma" : {'name' : 'Osmanya Digits (osma)', "digits" : "𐒠𐒡𐒢𐒣𐒤𐒥𐒦𐒧𐒨𐒩"},
        "rohg" : {'name' : 'Hanifi Rohingya digits (rohg)', "digits" : "𐴰𐴱𐴲𐴳𐴴𐴵𐴶𐴷𐴸𐴹"},
        "saur" : {'name' : 'Saurashtra Digits (saur)', "digits" : "꣐꣑꣒꣓꣔꣕꣖꣗꣘꣙"},
        "shrd" : {'name' : 'Sharada Digits (shrd)', "digits" : "𑇐𑇑𑇒𑇓𑇔𑇕𑇖𑇗𑇘𑇙"},
        "sind" : {'name' : 'Khudabadi Digits (sind)', "digits" : "𑋰𑋱𑋲𑋳𑋴𑋵𑋶𑋷𑋸𑋹"},
        "sinh" : {'name' : 'Sinhala Digits (sinh)', "digits" : "෦෧෨෩෪෫෬෭෮෯"},
        "sora" : {'name' : 'Sora Sompeng Digits (sora)', "digits" : "𑃰𑃱𑃲𑃳𑃴𑃵𑃶𑃷𑃸𑃹"},
        "sund" : {'name' : 'Sundanese Digits (sund)', "digits" : "᮰᮱᮲᮳᮴᮵᮶᮷᮸᮹"},
        "takr" : {'name' : 'Takri Digits (takr)', "digits" : "𑛀𑛁𑛂𑛃𑛄𑛅𑛆𑛇𑛈𑛉"},
        "talu" : {'name' : 'New Tai Lue Digits (talu)', "digits" : "᧐᧑᧒᧓᧔᧕᧖᧗᧘᧙"},
        "tamldec" : {'name' : 'Tamil Digits (tamldec)', "digits" : "௦௧௨௩௪௫௬௭௮௯"},
        "tnsa" : {'name' : 'Tangsa Digits (tnsa)', "digits" : "𖫀𖫁𖫂𖫃𖫄𖫅𖫆𖫇𖫈𖫉"},
        "telu" : {'name' : 'Telugu Digits (telu)', "digits" : "౦౧౨౩౪౫౬౭౮౯"},
        "thai" : {'name' : 'Thai Digits (thai)', "digits" : "๐๑๒๓๔๕๖๗๘๙"},
        "tibt" : {'name' : 'Tibetan Digits (tibt)', "digits" : "༠༡༢༣༤༥༦༧༨༩"},
        "tirh" : {'name' : 'Tirhuta Digits (tirh)', "digits" : "𑓐𑓑𑓒𑓓𑓔𑓕𑓖𑓗𑓘𑓙"},
        "vaii" : {'name' : 'Vai Digits (vaii)', "digits" : "꘠꘡꘢꘣꘤꘥꘦꘧꘨꘩"},
        "wara" : {'name' : 'Warang Citi Digits (wara)', "digits" : "𑣠𑣡𑣢𑣣𑣤𑣥𑣦𑣧𑣨𑣩"},
        "wcho" : {'name' : 'Wancho Digits (wcho)', "digits" : "𞋰𞋱𞋲𞋳𞋴𞋵𞋶𞋷𞋸𞋹"}
        #"hanidec" : {'name' : 'Chinese Decimal Numerals (hanidec)', "digits": '', "sep_out": [",", "."]}
    }
    try:
        sep = data[system_out]['sep_out']
    except KeyError:
        sep = sep_out
    t = n.maketrans(data[system_in]["digits"], data[system_out]["digits"])
    _locale.setlocale(_locale.LC_ALL, "")
    return n.translate(t).replace("ṯ", sep[0] ).replace("ḏ", sep[1])


#
# convert_to_arab_ns()
#
#    Convert numerals from Western Arabic numerals to Eastern Arabic numerals.
#    A numeral system (ns) specific version of convert_numeral_systems().
#
#    Returns a string
#

def convert_to_arab_ns(n, p=None, decimal=2, sep_in=["", "."], sep_out=["\u066C", "\u066B"], scale=None):
    _locale.setlocale(_locale.LC_ALL, "en_US.UTF-8")
    decimal_places = decimal
    if sep_in == ["", "."]:
        n = n * scale if scale else n
        format_string = '%0.' + str(decimal_places) + 'f' if type(n) == float else '%d'
        n = _locale.format_string(format_string, n, grouping=True, monetary=True)
        n = n.replace(",", "ṯ").replace(".", "ḏ")
    if sep_in[0] in [" ", ",", "٬", "\u2009", "\u202F"]:
        n = n.replace(r'[\u0020,٬\u2009\u202F]', "ṯ")
    elif sep_in[0] == ".":
        n = n.replace(".", "ṯ")
    if sep_in[1] in [",", ".", "٫"]:
        n = n.replace(r'[,.٫]', "ḏ")
    #sep = sep_out
    t = n.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    _locale.setlocale(_locale.LC_ALL, "")
    return n.translate(t).replace("ṯ", sep_out[0] ).replace("ḏ", sep_out[1])

convert_to_kurdish_ns = convert_to_arab_ns

#
# _icu._icu.Locale formatted numbers using PyICU
#   Supports both integers and floating point numbers.
#
# Usage:
#   _icu_formatted_digits(112345.05)
#   _icu_formatted_digits(112345.05, loc=_icu._icu.Locale.getFrench())
#   _icu_formatted_digits(112345.05, loc=_icu._icu.Locale("hi_IN@numbers=deva"))
#   _icu_formatted_digits(112345.05, loc=_icu._icu.Locale.forLanguageTag("my-MM-u-nu-mymr"))
#   _icu_formatted_digits(112345.05, loc=_icu._icu.Locale("ckb_IQ@numbers=arab"))
#   _icu_formatted_digits(112345.05, loc=_icu._icu.Locale.forLanguageTag("ckb-IQ-u-nu-arab"))
#   _icu_formatted_digits(112345.05, loc=_icu._icu.Locale.forLanguageTag("ckb-IR-u-nu-arabext"))


def _icu_formatted_digits(digit, p=None, loc=_icu.Locale.getRoot()):
    """_summary_

    Args:
        digit (int or float): _description_
        p (int, optional): Precision. Defaults to None.
        loc (_icu.Locale, optional): Locale object for formatted numbers. Defaults to _icu Root Locale.

    Returns:
        _type_: _description_
    """
    # TODO:
    #   * add support for precision
    if loc is None:
        loc = _icu.Locale.getRoot()
    if int(_icu.ICU_MAX_MAJOR_VERSION) >= 60:
        formatter = _icu.LocalizedNumberFormatter(loc)
        r = formatter.formatDouble(digit) if isinstance(digit, float) else formatter.formatInt(digit)
    else:
        formatter = _icu.NumberFormat.createInstance(loc)
        r = formatter.format(digit)
    return r

# EXAMPLES
#
# import el_internationalisation as eli
#
# eli.convert_digits('٩٢٦٥')
# 9265
# eli.convert_digits('٩٢٦٥', use_icu=True)
# 9265
#
# eli.convert_digits('٣٫١٤١٥٩٢٦٥٣٥٨', sep=('', "\u066B"))
# 3.14159265358
# eli.convert_digits('٣٫١٤١٥٩٢٦٥٣٥٨', sep=('', "\u066B"), use_icu=True)
# 3.14159265358
#
# _icu_formatted_digits(1234563133, loc=_icu.Locale('en_IN'))
# '1,23,45,63,133'
#
# _icu_formatted_digits(1234563133, loc=_icu.Locale('hi_IN'))
# '1,23,45,63,133'
#
# _icu_formatted_digits(1234563133, loc=_icu.Locale.forLanguageTag('hi-IN-u-nu-deva'))
# '१,२३,४५,६३,१३३'
#
# locale = _icu.Locale.forLanguageTag(lang)
# _icu_formatted_digits(12345, loc=locale)
# '१२,३४५'

