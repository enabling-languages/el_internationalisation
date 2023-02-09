##########################################################
# el_strings
#
#   © Enabling Languages 2022
#   Released under the MIT License.
#
##########################################################

import regex
import unicodedataplus
import icu

# from icu import icu.UnicodeString, icu.Locale, icu.Normalizer2, icu.UNormalizationMode2

# TODO:
#   * add type hinting
#   * add DocStrings

####################
# isalpha()
#
#    Add Mn and Mc categories and interpunct to Unicode Alphabetic derived property
#    Mode determines how alphabetic characters are detected. None or 'el' uses custom
#    isalpha() that is based on Unicode Alphabetic derived property, and adds
#    Mn and Mc categories and interpunct.
#    'unicode' uses the Unicode definition of alphabetic characters.
#    'core' uses the Python3 definition.
#
####################
def isalpha(text, mode=None):
    if (not mode) or (mode.lower() == "el"):
        if len(text) == 1:
            result = bool(regex.match(r'[\p{Alphabetic}\p{Mn}\p{Mc}\u00B7]', text))
        else:
            result = bool(regex.match(r'^\p{Alphabetic}[\p{Alphabetic}\p{Mn}\p{Mc}\u00B7]*$', text))
    elif mode.lower() == "unicode":
        result = bool(regex.match(r'^\p{Alphabetic}+$', text))        # Unicode Alphabetic derived property
    else:
        result = text.isalpha()          # core python3 isalpha()
    return result

# Unicode Alphabetic derived property
def isalpha_unicode(text):
    return bool(regex.match(r'^\p{Alphabetic}+$', text))

####################
#
# Unicode normalisation
#   Simple wrappers for Unicode normalisation
#
####################

def toNFD(text, use_icu=False):
    if use_icu:
        normaliser = icu.Normalizer2.getNFDInstance()
        return normaliser.normalize(text)
    return unicodedataplus.normalize("NFD", text)
NFD = toNFD

def toNFKD(text, use_icu=False):
    if use_icu:
        normaliser = icu.Normalizer2.getNFKDInstance()
        return normaliser.normalize(text)
    return unicodedataplus.normalize("NFKD", text)
NFKD = toNFKD

def toNFC(text, use_icu=False):
    if use_icu:
        normaliser = icu.Normalizer2.getNFCInstance()
        return normaliser.normalize(text)
    return unicodedataplus.normalize("NFC", text)
NFC = toNFC

def toNFKC(text, use_icu=False):
    if use_icu:
        normaliser = icu.Normalizer2.getNFKCInstance()
        return normaliser.normalize(text)
    return unicodedataplus.normalize("NFKC", text)
NFKC = toNFKC

def toNFKC_Casefold(text, use_icu=False):
    if use_icu:
        normaliser = icu.Normalizer2.getNFKCCasefoldInstance()
        return normaliser.normalize(text)
    pattern = regex.compile(r"\p{Default_Ignorable_Code_Point=Yes}")
    text = regex.sub(pattern, '', text)
    return unicodedataplus.normalize("NFC", unicodedataplus.normalize('NFKC', text).casefold())
NFKC_CF = toNFKC_Casefold

def toCasefold(text, use_icu=False):
    if use_icu:
        return str(icu.UnicodeString(text).foldCase())
    return  text.casefold()
fold_case = toCasefold

# Replace values matching dictionary keys with values
def replace_all(text, pattern_dict):
    for key in pattern_dict.keys():
        text = text.replace(key, str(pattern_dict[key]))
    return text

# Normalise to specified Unicode Normalisation Form, defaulting to NFC.
# nf = NFC | NFKC | NFKC_CF | NFD | NFKD | NFM21
# NFM21: Normalise strings according to MARC21 Character repetoire requirements

def normalise(nf, text):
    nf = nf.upper()
    if nf not in ["NFC", "NFKC", "NFKC_CF", "NFD", "NFKD", "NFM21"]:
        nf="NFC"
    # MNF (Marc Normalisation Form)
    def marc21_normalise(text):
        # Normalise to NFD
        text = unicodedataplus.normalize("NFD", text)
        # Latin variations between NFD and MNF
        latn_rep = {
            "\u004F\u031B": "\u01A0",
            "\u006F\u031B": "\u01A1",
            "\u0055\u031B": "\u01AF",
            "\u0075\u031B": "\u01B0"
        }
        # Cyrillic variations between NFD and MNF
        cyrl_rep = {
            "\u0418\u0306": "\u0419",
            "\u0438\u0306": "\u0439",
            "\u0413\u0301": "\u0403",
            "\u0433\u0301": "\u0453",
            "\u0415\u0308": "\u0401",
            "\u0435\u0308": "\u0451",
            "\u0406\u0308": "\u0407",
            "\u0456\u0308": "\u0457",
            "\u041A\u0301": "\u040C",
            "\u043A\u0301": "\u045C",
            "\u0423\u0306": "\u040E",
            "\u0443\u0306": "\u045E"
        }
        # Arabic variations between NFD and MNF
        arab_rep = {
            "\u0627\u0653": "\u0622",
            "\u0627\u0654": "\u0623",
            "\u0648\u0654": "\u0624",
            "\u0627\u0655": "\u0625",
            "\u064A\u0654": "\u0626"
        }
        # Only process strings containing characters that need replacing
        if bool(regex.search(r'[ouOU]\u031B', text)):
            text = replace_all(text, latn_rep)
        if bool(regex.search(r'[\u0413\u041A\u0433\u043A]\u0301|[\u0418\u0423\u0438\u0443]\u0306|[\u0406\u0415\u0435\u0456]\u0308', text)):
            text = replace_all(text, cyrl_rep)
        if bool(regex.search(r'[\u0627\u0648\u064A]\u0654|\u0627\u0655|\u0627\u0653', text)):
            text = replace_all(text, arab_rep)
        return text
    if nf == "NFM21":
        return marc21_normalise(text)
    elif nf == "NFKC_CF":
        return toNFKC_Casefold(text)
    return unicodedataplus.normalize(nf, text)

####################
#
# Unicode matching
#
####################

# Caseless matching
#   toCasefold(X) = toCasefold(Y)
def caseless_match(x, y, use_icu=False):
    return toCasefold(x, use_icu=use_icu) == toCasefold(y, use_icu=use_icu)

# Canonical caseless matching
#   NFD(toCasefold(NFD(X))) = NFD(toCasefold(NFD(Y)))
def canonical_caseless_match_icu(x, y, use_icu=False):
    return toNFD(toCasefold(toNFD(x, use_icu=use_icu), use_icu=use_icu), use_icu=use_icu) == toNFD(toCasefold(toNFD(y, use_icu=use_icu), use_icu=use_icu), use_icu=use_icu)

# Compatibility caseless match
#   NFKD(toCasefold(NFKD(toCasefold(NFD(X))))) = NFKD(toCasefold(NFKD(toCasefold(NFD(Y)))))
def compatibility_caseless_match(x, y, use_icu=False):
    return toNFKD(toCasefold(toNFKD(toCasefold(toNFD(x, use_icu=use_icu), use_icu=use_icu), use_icu=use_icu), use_icu=use_icu), use_icu=use_icu) == toNFKD(toCasefold(toNFKD(toCasefold(toNFD(y, use_icu=use_icu), use_icu=use_icu), use_icu=use_icu), use_icu=use_icu), use_icu=use_icu)

# Identifier caseless match for a string Y if and only if: 
#   toNFKC_Casefold(NFD(X)) = toNFKC_Casefold(NFD(Y))`
def identifier_caseless_match(x, y, use_icu=False):
    return toNFKC_Casefold(toNFD(x, use_icu=use_icu)) == toNFKC_Casefold(toNFD(y, use_icu=use_icu))


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
    return bool(regex.findall(pattern, text))

def clean_presentation_forms(text, folding=False):
    def clean_pf(match, folding):
        return  match.group(1).casefold() if folding else unicodedataplus.normalize("NFKC", match.group(1))
    pattern = r'([\p{InAlphabetic_Presentation_Forms}\p{InArabic_Presentation_Forms-A}\p{InArabic_Presentation_Forms-B}]+)'
    return regex.sub(pattern, lambda match, folding=folding: clean_pf(match, folding), text)

####################
#
# Turkish casing implemented without module dependencies.
# PyICU provides a more comprehensive solution for Turkish.
#
####################

# To lowercase
def kucukharfyap(s):
    return unicodedataplus.normalize("NFC", s).replace('İ', 'i').replace('I', 'ı').lower()

# To uppercase
def buyukharfyap(s):
    return unicodedataplus.normalize("NFC", s).replace('ı', 'I').replace('i', 'İ').upper()

####################
#
# PyICU Helper functions for casing and casefolding.
# s is a string, l is an ICU Locale object (defaulting to CLDR Root Locale)
#
####################

def toLower(s, use_icu=True, loc=icu.Locale.getRoot()):
    if not use_icu:
        return s.lower()
    return str(icu.UnicodeString(s).toLower(loc))

def toUpper(s, use_icu=True, loc=icu.Locale.getRoot()):
    if not use_icu:
        return s.upper()
    return str(icu.UnicodeString(s).toUpper(loc))

def toTitle(s, use_icu=True, loc=icu.Locale.getRoot()):
    if not use_icu:
        return s.title()
    return str(icu.UnicodeString(s).toTitle(loc))

TURKIC = ["tr", "az"]

def toSentence(s, engine="core", lang="und"):
    # loc = icu.Locale.forLanguageTag(lang)
    lang = regex.split('[_\-]', lang.lower())[0]
    result = ""
    if (engine == "core") and (lang in TURKIC):
        result = buyukharfyap(s[0]) + kucukharfyap(s[1:])
    elif (engine == "core") and (lang not in TURKIC):
        result = s.capitalize()
    elif engine == "icu":
        if lang not in list(icu.Locale.getAvailableLocales().keys()):
            lang = "und"
        loc = icu.Locale.getRoot() if lang == "und" else icu.Locale.forLanguageTag(lang)
        result = str(icu.UnicodeString(s[0]).toUpper(loc)) + str(icu.UnicodeString(s[1:]).toLower(loc))
    else:
        result = s
    return result

# New verion of toSentence
# def toSentence(s, lang="und", use_icu=False):
#     lang_subtag = regex.split('[_\-]', lang.lower())[0]
#     result = ""
#     if not use_icu and lang_subtag in TURKIC:
#         return buyukharfyap(s[0]) + kucukharfyap(s[1:])
#     elif not use_icu and lang_subtag in TURKIC:
#         return s.capitalize()
#     if lang_subtag not in list(icu.Locale.getAvailableLocales().keys()):
#         lang = "und"
#     loc = icu.Locale.getRoot() if lang == "und" else icu.Locale.forLanguageTag(lang)
#     result = str(icu.UnicodeString(s[0]).toUpper(loc)) + str(icu.UnicodeString(s[1:]).toLower(loc))
#     return result

def foldCase(s, engine="core"):
    result = ""
    if engine == "core":
        result = s.casefold()
    elif engine == "icu":
        result = str(icu.UnicodeString(s).foldCase())
    else:
        result = s
    return result


####################
#
# graphemes():
#   Create a list of extended grapheme clusters in a string.
#
####################
def graphemes(text):
    return regex.findall(r'\X',text)
gr = graphemes