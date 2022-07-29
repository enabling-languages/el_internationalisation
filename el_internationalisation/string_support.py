##########################################################
# el_strings
#
#   © Enabling Languages 2022
#   Released under the MIT License.
#
##########################################################

import regex, unicodedataplus, icu
# from icu import icu.UnicodeString, icu.Locale, icu.Normalizer2, icu.UNormalizationMode2

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
# Unicode matching
#
####################

def caseless_match(x, y):
  return x.casefold() == y.casefold()

def canonical_caseless_match(x, y):
  return unicodedataplus.normalize("NFD", unicodedataplus.normalize("NFD", x).casefold()) == unicodedataplus.normalize("NFD", unicodedataplus.normalize("NFD", y).casefold())

def compatibility_caseless_match(x, y):
  return unicodedataplus.normalize("NFKD", unicodedataplus.normalize("NFKD", unicodedataplus.normalize("NFD", x).casefold()).casefold()) == unicodedataplus.normalize("NFKD", unicodedataplus.normalize("NFKD", unicodedataplusnormalize("NFD", y).casefold()).casefold())

def NFKC_Casefold(s):
  return unicodedataplus.normalize("NFC", unicodedataplus.normalize('NFKC', s).casefold())

NFKC_CF = NFKC_Casefold

def identifier_caseless_match(x, y):
  return NFKC_Casefold(unicodedataplus.normalize("NFD", x)) == NFKC_Casefold(unicodedataplus.normalize("NFD", y))

####################
#
# Unicode normalisation
#   Simple wrappers for Unicode normalisation
#
####################

def NFD(s, engine="ud"):
    if engine.lower() == "icu":
        normalizer = icu.Normalizer2.getInstance(None, "nfc", icu.UNormalizationMode2.DECOMPOSE)
        return normalizer.normalize(s)
    return unicodedataplus.normalize('NFD', s)

def NFKD(s, engine="ud"):
    if engine.lower() == "icu":
        normalizer = icu.Normalizer2.getInstance(None, "nfkc", icu.UNormalizationMode2.DECOMPOSE)
        return normalizer.normalize(s)
    return unicodedataplus.normalize('NFKD', s)

def NFC(s, engine="ud"):
    if engine.lower() == "icu":
        normalizer = icu.Normalizer2.getInstance(None, "nfc", icu.UNormalizationMode2.COMPOSE)
        return normalizer.normalize(s)
    return unicodedataplus.normalize('NFC', s)

def NFKC(s, engine="ud"):
    if engine.lower() == "icu":
        normalizer = icu.Normalizer2.getInstance(None, "nfkc", icu.UNormalizationMode2.COMPOSE)
        return normalizer.normalize(s)
    return unicodedataplus.normalize('NFKC', s)

# Normalise to specified Unicode Normalisation Form, defaulting to NFC.
# nf = NFC | NFKC | NFD | NFKD | NFM
# NFM: Normalise strings according to MARC21 Character repetoire requirements
# TODO:
#    * Add support for NFKC_CF

# Replace values matching dictionary keys with values
def replace_all(text, pattern_dict):
    for key in pattern_dict.keys():
        text = text.replace(key, str(pattern_dict[key]))
    return text

def normalise(nf, text):
    nf = nf.upper()
    if nf not in ["NFC", "NFKC", "NFD", "NFKD", "NFM"]:
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
    if nf == "NFM":
        return marc21_normalise(text)
    return unicodedataplus.normalize(nf, text)


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
# PyICU Helper functions for casing and casefolding.
# s is a string, l is an ICU Locale object (defaulting to CLDR Root Locale)
#
####################

def toLower(s, l=icu.Locale.getRoot()):
    return str(icu.UnicodeString(s).toLower(l))
def toUpper(s, l=icu.Locale.getRoot()):
    return str(icu.UnicodeString(s).toUpper(l))
def toTitle(s, l=icu.Locale.getRoot()):
    return str(icu.UnicodeString(s).toTitle(l))
def toSentence(s, l=icu.Locale.getRoot()):
    return(str(icu.UnicodeString(s[0]).toUpper(l)) + str(icu.UnicodeString(s[1:]).toLower(l)))
def foldCase(s):
    return str(icu.UnicodeString(s).foldCase())

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
# graphemes():
#   Create a list of extended grapheme clusters in a string.
#
####################
def graphemes(text):
    return regex.findall(r'\X',text)
gr = graphemes