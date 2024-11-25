##########################################################
# el_internationalisation.ustrings
#
#   © Enabling Languages 2023-2024
#   Released under the MIT License.
#
##########################################################

from collections import Counter as _Counter, UserString as _UserString
from collections.abc import Sequence as _Sequence
import icu as _icu
import regex as _regex
import unicodedataplus as _unicodedataplus
from .bidi import bidi_envelope, is_bidi, first_strong, dominant_strong_direction
from functools import partial as _partial
from wcwidth import wcswidth as _wcswidth
from el_data import EthiopicUCDString as _Ethi, udata
try:
  from typing import Self as _Self
except ImportError:
  from typing_extensions import Self as _Self
from typing import Generator as _Generator, TypeAlias as _TypeAlias
from datetime import datetime

Char: _TypeAlias = tuple[str, str, str]
# type Char = tuple[str, str, str]
CharData: _TypeAlias = list[Char]
# type CharData = list[Char]

# TODO:
#   * add type hinting
#   * add DocStrings

VERSION = "0.7.5"
UD_VERSION = _unicodedataplus.unidata_version
ICU_VERSION = _icu.ICU_VERSION
PYICU_VERSION = _icu.VERSION
ICU_UNICODE_VERSION = _icu.UNICODE_VERSION

####################
#
# Utility functions
#
####################

def empty_or_none(x):
    return x is None or x in ['', ' ']

def count_characters(text, localeID, auxiliary=False, to_dict=False):
      c = _Counter(text)
      uld = _icu.LocaleData(localeID)
      exemplar_us = uld.getExemplarSet(4, 0)
      if auxiliary:
            auxiliary_us = uld.getExemplarSet(4, 1)
            exemplar_us.addAll(auxiliary_us)
      punctuation_us = uld.getExemplarSet(0, 3)
      exemplar_us.addAll(punctuation_us)
      us_iter = _icu.UnicodeSetIterator(exemplar_us)
      for i in us_iter:
            if not c[i]:
                  c[i] = 0
      return dict(c) if to_dict else c

def count_ngraphs(text, ngram_length=2):
      return _Counter(text[idx : idx + ngram_length] for idx in range(len(text) - 1))

####################
# analyse characters
#  Functions to assist in analysing Unicode strings, and assist in debugging encoding issues.
#
#
####################

def splitString(text):
    """Typecast string to a list, splitting sting into a list of characters.
    Character level tokenisation.

    Args:
        text (str): Unicode string to be tokenised.

    Returns:
        list: a list of single Unicode character tokens.
    """
    return list(text)

def utf8len(text):
    """Number of bytes required when string is using UTF-8 encoding.

    Args:
        text (str): String to be analysed

    Returns:
        int: number of bytes in UTF-8 encoded string.
    """
    return len(text.encode('utf-8'))

def utf16len(text):
    """Number of bytes required when string is using UTF-16 LE or BE encoding.

    Args:
        text (str): String to be analysed

    Returns:
        int: number of bytes in UTF-16 LE or BE encoded string.
    """
    return len(text.encode('utf-16-le'))

def add_dotted_circle(text):
    """Add dotted circle to combining diacritics in a string.

    Args:
        text (str): string to parse

    Returns:
        str: transformed string with combining diacritics in string applied to a dotted circle.
    """
    return "".join(["\u25CC" + i if _unicodedataplus.combining(i) else i for i in list(text)])

# codepoints and characters in string
#
# Usage:
#    eli.codepoints("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪")
#    eli.cp("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪", extended=True)
#    eli.cp("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪", prefix=True, extended=True)

def codepoints(text: str, prefix: bool = False, extended: bool = False) -> str | _Sequence[CharData]:
    """Identifies codepoints in a string.

    Args:
        text (str): string to analyse.
        prefix (bool, optional): flag indicating if the U+ prefix is appended to codepoint. Defaults to False.
        extended (bool, optional): flag indicating if character is displayed after codepoint. Defaults to False.

    Returns:
        str | _Sequence[CharData]: string of Unicode codepoints in analysed string, or if extended a list of tuples containing teh character, codepoint, and character name
    """
    if extended:
        return [(c, f"U+{ord(c):04X}", _unicodedataplus.name(c)) for c in text] if prefix else [(c, f"{ord(c):04X}", _unicodedataplus.name(c)) for c in text]
    else:
        # return ' '.join('U+{:04X}'.format(ord(c)) for c in text) if prefix else ' '.join('{:04X}'.format(ord(c)) for c in text)
        return ' '.join(f"U+{ord(c):04X}" for c in text) if prefix else ' '.join(f"{ord(c):04X}" for c in text)
cp = codepoints

def codepointsToChar(codepoints):
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
    cplist = _regex.split(r",\s*|\s+", codepoints)
    return "".join([chr(int(c, 16)) for c in cplist])
    # return "".join([chr(int(i.removeprefix('u+'), 16)) for i in _regex.split(r'[,;]\s?|\s+', cps.lower())])

def canonical_equivalents_str(ustring):
    """List canonically equivalent strings for given string.

    Args:
        ustring (str): character, grapheme or short string to analyse.

    Returns:
        List[str]: list of all canonically equivalent forms of ustring.
    """
    ci =  _icu.CanonicalIterator(ustring)
    return [' '.join(f"U+{ord(c):04X}" for c in char) for char in ci]

def canonical_equivalents(ci, ustring = None):
    """List canonically equivalent strings for given canonical iterator instance.

    Args:
        ci (_icu.CanonicalIterator): a CanonicalIterator instance.

    Returns:
        List[str]: list of all canonically equivalent forms of ustring.
    """
    if ustring:
        ci.setSource(ustring)
    return [' '.join(f"U+{ord(c):04X}" for c in char) for char in ci]

# def unicode_data(text, ce=False):
#     """Display Unicode data for each character in string.
# 
#     Perform a character tokenisation on a string, and generate a table containing
#     data on some Unicode character properties, including character codepoint and name,
#     script character belongs to,
# 
#     Args:
#         text (str): string to analyse.
#     """
#     print(f"String: {text}")
#     t = prettytable.PrettyTable(["char", "cp", "name", "script", "block", "cat", "bidi", "cc"])
#     for c in list(text):
#         if _unicodedataplus.name(c,'-')!='-':
#             cr = bidi_envelope(c, dir="auto", mode="isolate") if is_bidi(c) else c
#             t.add_row([cr, "%04X"%(ord(c)),
#                 _unicodedataplus.name(c,'-'),
#                 _unicodedataplus.script(c),
#                 _unicodedataplus.block(c),
#                 _unicodedataplus.category(c),
#                 _unicodedataplus.bidirectional(c),
#                 _unicodedataplus.combining(c)])
#     print(t)
#     if ce:
#         print(canonical_equivalents_str(text))
#     return None
# 
# udata = unicode_data

def codepoint_names(text):
    return [(f"U+{ord(c):04X}", _unicodedataplus.name(c,'-')) for c in text]

cpnames = codepoint_names

def print_list(in_list, sep ="\n"):
    # print('\n'.join([ str(element) for element in in_list ]))
    print(*in_list, sep=sep)

printl = print_list

# text = "ꗏ ꕘꕞꘋ ꔳꕩ"
# printl(cpname(text))

def isScript(text:str , script:str , common:bool=False) -> bool:
    """Test if characters in string belong to specified script.

    Args:
        text (str): String to test.
        script (str): Script to match against.
        common (bool, optional): Include characters classified as Common in match. Defaults to False.

    Returns:
        bool: Result of string tested against specified script.
    """
    pattern_string = r'^[\p{' + script + r'}\p{Common}]+$' if common else r'^\p{' + script + r'}+$'
    pattern = _regex.compile(pattern_string)
    return bool(_regex.match(pattern, text))

def dominant_script(text, mode="individual"):
    count = _Counter([_unicodedataplus.script(char) for char in text])
    total = sum(count.values())
    if mode == "all":
        return [(i, count[i]/total) for i in list(count)]
    dominant = (count.most_common(2)[0][0], count.most_common(2)[0][1]/total) if count.most_common(2)[0][0] != "Common" else (count.most_common(2)[1][0],  count.most_common(2)[1][1]/total)
    return dominant

class ngraphs:
    """Calculate ngraph occurrences for target string

    Attributes
    ----------
    text: str
        A plain text string to be analysed. Specific to ngraph instance.
    size: int
        Size of ngraph. 2 = digraph, 3 = character, etc. Defaults to 2
    filter: bool
        Filter out punctuation and whitespace, so that these characters do not appear
        in the ngraphs. Defaults to False
    count: int
    graphemes: bool
        Whether ngraphs are calculated on basis of number of characters, or number of graphemes.
        Defaults to False.


    Methods
    -------
    most_common()
        Dictionary containing the _count_ most frequent ngraphs. Returns dictionary of
        ngraphs, count of occurrence of ngraphs.

    ngraph_list()
        Return list of ngraphs generated from _text_.
    """

    def __init__(self, text, size=2, filter=False, count=10, graphemes=False):
        self._text = text
        self.size = size
        self.filter = filter
        self.count = count
        self.graphemes = graphemes
        self.data

    @property
    def data(self):
        self._data = self._frequency()
        return self._data

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        # self._text = value
        raise Exception("Cannot set text. Require new instance of ngraphs.")

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, value):
        self._filter = value

    @property
    def grapheme(self):
        return self._grapheme

    @grapheme.setter
    def grapheme(self):
        return self._grapheme

    @grapheme.setter
    def grapheme(self, value):
        # self._grapheme = value
        raise Exception("Cannot set grapheme. Require new instance of ngraphs.")

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value

    def __str__(self):
        return f"size: {self.size} , filter: {self.filter} , count: {self.count}"

    def _frequency(self):
        # Identify ngraphs in text and count number of occurrences of each ngraph
        # pattern = f'[^\p\u007bP\u007d\p\u007bZ\u007d]\u007b{self.size}\u007d'
        pattern = r'[^\p{P}\p{Z}]{' + str(self.size) + r'}'
        r = {}
        if self.graphemes:
            gr = graphemes(self.text)
            c = {"".join(i for i in k): v for k, v in dict(_Counter(tuple(gr)[idx : idx + self.size] for idx in range(len(gr) - 1))).items()}
        else:
            c = _Counter(self.text[idx : idx + self.size] for idx in range(len(self.text) - 1))
        r = {x: count for x, count in c.items() if _regex.match(pattern, x)} if self.filter else dict(c)
        r = dict(sorted(r.items(), key=lambda x:x[1], reverse=True))
        return r
        # return {"size":self.size, "filter":self.filter ,"ngraths": r}

    # def _frequency_percentage(self, value):
    #     pdata = {k: round(v*100/self.total(), 6) for k,v in self.data.items()}
    #     return None

    # def _percentage(self, value):
    #    return round(value*100/self.total(), 4)

    def most_common(self, value=None):
        if value and value != self.count:
            self._count = value
        return dict(list(self.data.items())[0: self.count])

    def to_list(self):
        # Convert data keys to list, i.e. list of ngraphs
        return [i for i in self.data.keys()]

    def to_tuples(self):
        # Convert data dictionary to a list of tuples of ngraphs.
        # return [(k, v, self._percentage(v)) for k, v in self.data.items()]
        return [(k, v) for k, v in self.data.items()]

    def ngraph_length(self):
        # Number of unique ngraphs in data
        return len(self.data)

    def text_length(self):
        # Length (number of characters) of text
        return len(self.text)

    def total(self):
        # Total number of ngraphs available in string
        return sum(self.data.values())

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
def isalpha(text, mode="unicode"):
    if (not mode) or (mode.lower() == "el"):
        if len(text) == 1:
            result = bool(_regex.match(r'[\p{Alphabetic}\p{Mn}\p{Mc}\u00B7]', text))
        else:
            result = bool(_regex.match(r'^\p{Alphabetic}[\p{Alphabetic}\p{Mn}\p{Mc}\u00B7]*$', text))
    elif mode.lower() == "unicode":
        result = bool(_regex.match(r'^\p{Alphabetic}+$', text))        # Unicode Alphabetic derived property
    else:
        result = text.isalpha()          # core python3 isalpha()
    return result

# Unicode Alphabetic derived property
def isalpha_unicode(text):
    return bool(_regex.match(r'^\p{Alphabetic}+$', text))

####################
#
# Word forming characters
#   Test for wether all characters in string consit of word forming characters.
#   Definition is based on Unicode definition for the regular expresison metacharacter \w
#   Optional support for hyphens, apostophe, interpunct.
#
####################

def is_word_forming(text: str, extended: bool = False) -> bool:
    """Test whether a string contains only word forming characters.

    Uses the definition in Unicode Regular Expressions UTD #18:
    '[\\p{alpha}\\p{gc=Mark}\\p{digit}\\p{gc=Connector_Punctuation}\\p{Join_Control}]'

    Optional support for hyphens, apostophe, interpunct.

    Args:
        text (str): string to test.
        extended (bool): Flag to specify whether word internal punctuation is considered word forming.

    Returns:
        bool: result, either True or False.
    """
    pattern = r'\p{alpha}\p{gc=Mark}\p{digit}\p{gc=Connector_Punctuation}\p{Join_Control}'
    if len(text) == 1:
        extended = False
    if extended:
        pattern = r'\p{alpha}\p{gc=Mark}\p{digit}\p{gc=Connector_Punctuation}\p{Join_Control}\u002D\u002E\u00B7'
    if len(text) == 1:
        return bool(_regex.match(f'[{pattern}]', text))
    return bool(_regex.match(f'^[{pattern}]*$', text))

####################
#
# Unicode normalisation
#   Simple wrappers for Unicode normalisation
#
####################

def register_transformation(id: str, rules: str, direction: int = _icu.UTransDirection.FORWARD) -> None:
    """Register a custom transliterator, allowing it to be reused.

    Args:
        id (str): id for transliterator, to be used with _icu.Transliterator.createInstance().
        rules (str): Transliteration/transformation rules. Refer to 
        direction (int, optional): Direction of transformation to be applied. Defaults to _icu.UTransDirection.FORWARD.

    Returns:
        None:
    """
    if id not in list(_icu.Transliterator.getAvailableIDs()):
        transformer = _icu.Transliterator.createFromRules(id, rules, direction)
        _icu.Transliterator.registerInstance(transformer)
    return None

def toNFD(text, use_icu=False):
    if use_icu:
        normaliser = _icu.Normalizer2.getNFDInstance()
        return normaliser.normalize(text)
    return _unicodedataplus.normalize("NFD", text)
NFD = toNFD

def toNFKD(text, use_icu=False):
    if use_icu:
        normaliser = _icu.Normalizer2.getNFKDInstance()
        return normaliser.normalize(text)
    return _unicodedataplus.normalize("NFKD", text)
NFKD = toNFKD

def toNFC(text, use_icu=False):
    if use_icu:
        normaliser = _icu.Normalizer2.getNFCInstance()
        return normaliser.normalize(text)
    return _unicodedataplus.normalize("NFC", text)
NFC = toNFC

def toNFKC(text, use_icu=False):
    if use_icu:
        normaliser = _icu.Normalizer2.getNFKCInstance()
        return normaliser.normalize(text)
    return _unicodedataplus.normalize("NFKC", text)
NFKC = toNFKC

def toNFKC_Casefold(text, use_icu=False):
    if use_icu:
        normaliser = _icu.Normalizer2.getNFKCCasefoldInstance()
        return normaliser.normalize(text)
    pattern = _regex.compile(r"\p{Default_Ignorable_Code_Point=Yes}")
    text = _regex.sub(pattern, '', text)
    return _unicodedataplus.normalize("NFC", _unicodedataplus.normalize('NFKC', text).casefold())
NFKC_CF = toNFKC_Casefold

def toCasefold(text: str, use_icu: bool = True, turkic: bool = False) -> str:
    if use_icu:
        option: int = 1 if turkic else 0
        # return str(_icu.UnicodeString(text).foldCase(option))
        return _icu.CaseMap.fold(option, text)
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

def is_hangul(s):
    return bool(_regex.search(r'(^\p{Hangul}+$)', s))
def normalise_hangul(s, normalisation_form = "NFC"):
    if is_hangul(s):
        return _unicodedataplus.normalize(normalisation_form, s)
    else:
        return s
def marc_hangul(text):
    return "".join(list(map(normalise_hangul, _regex.split(r'(\P{Hangul})', text))))

def normalise(nf, text, use_icu=False):
    nf = nf.upper()
    if nf not in ["NFC", "NFKC", "NFKC_CF", "NFD", "NFKD", "NFM21"]:
        nf="NFC"
    # MNF (Marc Normalisation Form)
    def marc21_normalise(text):
        # Normalise to NFD
        text = _unicodedataplus.normalize("NFD", text)
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
        if bool(_regex.search(r'[ouOU]\u031B', text)):
            text = replace_all(text, latn_rep)
        if bool(_regex.search(r'[\u0413\u041A\u0433\u043A]\u0301|[\u0418\u0423\u0438\u0443]\u0306|[\u0406\u0415\u0435\u0456]\u0308', text)):
            text = replace_all(text, cyrl_rep)
        if bool(_regex.search(r'[\u0627\u0648\u064A]\u0654|\u0627\u0655|\u0627\u0653', text)):
            text = replace_all(text, arab_rep)
        if bool(_regex.search(r'\p{Hangul}', text)):
            text = marc_hangul(text)
        return text
    if nf == "NFM21":
        if use_icu:
            transform_id = "toNFM21"
            nfm21_rules = (":: NFD; "
                ":: [\\p{Hangul}] NFC ; "
                "\u004F\u031B > \u01A0 ; \u008F\u031B > \u01A1 ; \u0055\u031B > \u01AF ; \u0075\u031B > \u01B0 ; "
                "\u0415\u0308 > \u0401 ; \u0435\u0308 > \u0451 ; \u0413\u0301 > \u0403 ; \u0433\u0301 > \u0453 ; "
                "\u0406\u0308 > \u0407 ; \u0456\u0308 > \u0457 ; \u041A\u0301 > \u040C ; \u043A\u0301 > \u045C ; "
                "\u0423\u0306 > \u040E ; \u0443\u0306 > \u045E ; \u0418\u0306 > \u0419 ; \u0438\u0306 > \u0439 ; "
                "\u0627\u0653 > \u0622 ; \u0627\u0654 > \u0623 ; \u0648\u0654 > \u0624 ; \u0627\u0655 > \u0625 ; "
                "\u064A\u0654 > \u0626 ; ")
            transform_direction = _icu.UTransDirection.FORWARD
            register_transformation(transform_id, nfm21_rules, transform_direction)
            transformer = _icu.Transliterator.createInstance(transform_id, transform_direction)
            return transformer.transliterate(text)
        else:
            return marc21_normalise(text)
    elif nf == "NFKC_CF":
        if use_icu:
            normaliser = _icu.Normalizer2.getNFKCCasefoldInstance()
        else:
            return toNFKC_Casefold(text)
    elif nf == "NFC" and use_icu:
        normaliser = _icu.Normalizer2.getNFCInstance()
    elif nf == "NFKC" and use_icu:
        normaliser = _icu.Normalizer2.getNFKCInstance()
    elif nf == "NFD" and use_icu:
        normaliser = _icu.Normalizer2.getNFDInstance()
    elif nf == "NFKD" and use_icu:
        normaliser = _icu.Normalizer2.getNFKDInstance()
    if use_icu:
        return normaliser.normalize(text)
    return _unicodedataplus.normalize(nf, text)

####################
#
# Unicode matching
#
####################

# Simple matching
#   NFD(X) = NFD(Y)
def simple_match(x, y, use_icu=False):
    return x == y

# Cased matching
#   toLower(NFD(X)) = toLower(NFD(Y))
# TODO:
#    add lowercaseing
def cased_match(x, y, use_icu=False):
    return toNFD(x, use_icu=use_icu) == toNFD(y, use_icu=use_icu)

# Caseless matching
#   toCasefold(X) = toCasefold(Y)
def caseless_match(x, y, use_icu=False):
    return toCasefold(x, use_icu=use_icu) == toCasefold(y, use_icu=use_icu)

# Canonical caseless matching
#   NFD(toCasefold(NFD(X))) = NFD(toCasefold(NFD(Y)))
def canonical_caseless_match(x, y, use_icu=False, turkic=False):
    return toNFD(toCasefold(toNFD(x, use_icu=use_icu), use_icu=use_icu, turkic=turkic), use_icu=use_icu) == toNFD(toCasefold(toNFD(y, use_icu=use_icu), use_icu=use_icu, turkic=turkic), use_icu=use_icu)

# Compatibility caseless match
#   NFKD(toCasefold(NFKD(toCasefold(NFD(X))))) = NFKD(toCasefold(NFKD(toCasefold(NFD(Y)))))
def compatibility_caseless_match(x, y, use_icu=False, turkic=False):
    return toNFKD(toCasefold(toNFKD(toCasefold(toNFD(x, use_icu=use_icu), use_icu=use_icu, turkic=turkic), use_icu=use_icu), use_icu=use_icu), use_icu=use_icu) == toNFKD(toCasefold(toNFKD(toCasefold(toNFD(y, use_icu=use_icu), use_icu=use_icu, turkic=turkic), use_icu=use_icu), use_icu=use_icu), use_icu=use_icu)

# Identifier caseless match for a string Y if and only if: 
#   toNFKC_Casefold(NFD(X)) = toNFKC_Casefold(NFD(Y))`
def identifier_caseless_match(x, y, use_icu=False, turkic=False):
    return toNFKC_Casefold(toNFD(x, use_icu=use_icu), use_icu=use_icu) == toNFKC_Casefold(toNFD(y, use_icu=use_icu), use_icu=use_icu)

####################
#
# Turkish casing implemented without module dependencies.
# PyICU provides a more comprehensive solution for Turkish.
#
####################

def multiple_replace(string, rep_dict):
    pattern = _regex.compile("|".join([_regex.escape(k) for k in sorted(rep_dict,key=len,reverse=True)]), flags=_regex.DOTALL)
    return pattern.sub(lambda x: rep_dict[x.group(0)], string)

tr_tolower_replacements = {'I':'ı', 'İ':'i'}
tr_toupper_replacements = {'ı':'I', 'i':'İ'}

# To lowercase
def trLower(text: str) -> str:
    text = normalise("NFC", text, use_icu=True)
    return multiple_replace(text, tr_tolower_replacements).lower()

def trCasefold(text: str) -> str:
    text = normalise("NFC", text, use_icu=True)
    return multiple_replace(text, tr_tolower_replacements).casefold()

# To uppercase
def trUpper(text:str) -> str:
    text = normalise("NFC", text, use_icu=True)
    return multiple_replace(text, tr_toupper_replacements).upper()

# To titlecase
def trTitle(text: str) -> str:
    text = normalise("NFC", text, use_icu=True)
    words: list[str] = text.split()
    tr_text: list[str] = []
    for word in words:
        tr_text.append(trUpper(word[0]) + trLower(word[1:]))
    return " ".join(tr_text)

# To Sentence casing
def trSentence(text: str) -> str:
    text = normalise("NFC", text, use_icu=True)
    words: list[str] = text.split(' ', 1)
    words[0] = trUpper(words[0])
    words[1] = trLower(words[1])
    return " ".join(words)

####################
#
# PyICU Helper functions for casing and casefolding.
# s is a string, l is an ICU Locale object (defaulting to CLDR Root Locale)
#
####################

def toLower(text: str, use_icu: bool = True, loc=_icu.Locale.getRoot()) -> str:
    if not use_icu:
        return text.lower()
    # return str(_icu.UnicodeString(text).toLower(loc))
    return _icu.CaseMap.toLower(loc, text)

def toUpper(text: str, use_icu: bool = True, loc=_icu.Locale.getRoot()) -> str:
    if not use_icu:
        return text.upper()
    # return str(_icu.UnicodeString(text).toUpper(loc))
    return _icu.CaseMap.toUpper(loc, text)

def toTitle(text: str, use_icu: bool = True, loc = _icu.Locale.getRoot()) -> str:
    if not use_icu:
        return text.title()
    # return str(_icu.UnicodeString(text).toTitle(loc))
    return _icu.CaseMap.toTitle(loc, 0, text)

def toSentence(text: str,  use_icu: bool = True, loc = _icu.Locale.getRoot()) -> str:
    if not use_icu:
        return text.capitalize()
    return _icu.CaseMap.toTitle(loc, 64, text)

capitalise = toSentence

TURKIC = ["tr", "az"]

#
# TODO:
#   * migrate form engine flag to use_icu flag for consistency
#
# def toSentence(s, engine="core", lang="und"):
#     # loc = _icu.Locale.forLanguageTag(lang)
#     # lang = _regex.split('[_\-]', lang.lower())[0]
#     lang = _regex.split(r'[_\-]', lang.lower())[0]
#     result = ""
#     if (engine == "core") and (lang in TURKIC):
#         result = buyukharfyap(s[0]) + kucukharfyap(s[1:])
#     elif (engine == "core") and (lang not in TURKIC):
#         result = s.capitalize()
#     elif engine == "_icu":
#         if lang not in list(_icu.Locale.getAvailableLocales().keys()):
#             lang = "und"
#         loc = _icu.Locale.getRoot() if lang == "und" else _icu.Locale.forLanguageTag(lang)
#         result = str(_icu.UnicodeString(s[0]).toUpper(loc)) + str(_icu.UnicodeString(s[1:]).toLower(loc))
#     else:
#         result = s
#     return result

# New verion of toSentence
# def toSentence(s, lang="und", use_icu=False):
#     lang_subtag = _regex.split('[_\-]', lang.lower())[0]
#     result = ""
#     if not use_icu and lang_subtag in TURKIC:
#         return buyukharfyap(s[0]) + kucukharfyap(s[1:])
#     elif not use_icu and lang_subtag not in TURKIC:
#         return s.capitalize()
#     if lang_subtag not in list(_icu.Locale.getAvailableLocales().keys()):
#         lang = "und"
#     loc = _icu.Locale.getRoot() if lang == "und" else _icu.Locale.forLanguageTag(lang)
#     result = str(_icu.UnicodeString(s[0]).toUpper(loc)) + str(_icu.UnicodeString(s[1:]).toLower(loc))
#     return result

#
# TODO:
#   * migrate form engine flag to use_icu flag for consistency
#
# def foldCase(s, engine="core"):
#     result = ""
#     if engine == "core":
#         result = s.casefold()
#     elif engine == "_icu":
#         result = str(_icu.UnicodeString(s).foldCase())
#     else:
#         result = s
#     return result


####################
#
# String prep
#
####################

def remove_punctuation(text):
    result = text.translate(str.maketrans('', '', "".join(list(_icu.UnicodeSet(r'[\p{P}]')))))
    return " ".join(result.strip().split())

def remove_digits(text):
    return _regex.sub(r"\d+([\u0020\u00A0\u202F]\d{3}|[\u066B\u066C,.'-]\d+)*", "", text).strip()

####################
#
# tokenise():
#   Create a list of tokens in a string.
#
####################

def get_boundaries(text, brkiter):
    brkiter.setText(text)
    boundaries = [*brkiter]
    boundaries.insert(0, 0)
    return boundaries

def tokenise(text, locale=_icu.Locale.getRoot(), mode="word"):
    """Tokenise a string based on locale: character, grapheme, word and sentense tokenisation supported.

    Args:
        text (_str_): string to tokenise.
        locale (__icu.Locale_, optional): _icu.Locale to use for tokenisation. Defaults to _icu.Locale.getRoot().
        mode (str, optional): Character, grapheme, word or sentense tokenisation to perform. Defaults to "word".

    Returns:
        _list_: list of tokens in string.
    """
    match mode.lower():
        case "character":
            return list(text)
        case "grapheme":
            bi = _icu.BreakIterator.createCharacterInstance(locale)
        case "sentence":
            bi = _icu.BreakIterator.createSentenceInstance(locale)
        case _:
            bi = _icu.BreakIterator.createWordInstance(locale)
    boundary_indices = get_boundaries(text, bi)
    return [text[boundary_indices[i]:boundary_indices[i+1]] for i in range(len(boundary_indices)-1)]

tokenize = tokenise

def tokenise_bi(text, brkiter):
    """Tokenise a string using specified break iterator.

    Args:
        text (_str_): string to tokenise.
        brkiter (__icu.BreakIterator_, optional): ICU break iterator to use for tokenisation.

    Returns:
        list: Tokens in string.
    """
    boundary_indices = get_boundaries(text, brkiter)
    return [text[boundary_indices[i]:boundary_indices[i+1]] for i in range(len(boundary_indices)-1)]

tokenize_bi = tokenise_bi

# Token generator
#     To get list of tokens:
#         iter = _icu.BreakIterator.createCharacterInstance(_icu.Locale('th_TH'))
#         [*gen_tokens(z, iter)]
#     or
#         list(gen_tokens(z, iter))

def generate_tokens(text: str, brkiter: _icu.RuleBasedBreakIterator | None = None) -> _Generator[str, None, None]:
    """Token generator: tokenise a string using specified break iterator

        Token generator
        To get list of tokens:
            iter = _icu.BreakIterator.createCharacterInstance(_icu.Locale('th_TH'))
            [*gen_tokens(z, iter)]
        or
            list(gen_tokens(z, iter))

    Args:
        text (str): String to be tokenised.
        brkiter (_icu.RuleBasedBreakIterator | None, optional): An ICU4C BreakIterator object. If None, then a word based break iterator for the Root locale will be used.. Defaults to None.

    Returns:
        str: Textual data to be tokenised.

    Yields:
        Iterator[str]: A generator for tokens.
    """
    if not brkiter:
        brkiter = _icu.BreakIterator.createWordInstance(_icu.Locale.getRoot())
    brkiter.setText(text)
    i = brkiter.first()
    for j in brkiter:
        yield text[i:j]
        i = j


def get_generated_tokens(text:str, bi: _icu.BreakIterator | None = None) -> list[str]:
    """Create a list of tokens from a generator

    Args:
        text (str): String to be tokenised.
        bi (_icu.BreakIterator | None, optional):  An ICU4C BreakIterator object. If None, then a word based break iterator for the Root locale will be used.. Defaults to None.

    Returns:
        list[str]: List of tokens based on specified break iterator.
    """
    #return [*gen_tokens(text, brkiter=bi)]
    return list(generate_tokens(text, brkiter=bi))

####################
#
# graphemes():
#   Create a list of extended grapheme clusters in a string.
#
####################
# def graphemes(text):
#     return _regex.findall(r'\X',text)

graphemes = _partial(tokenise, mode="grapheme")
graphemes.__doc__ = """Grapheme tokenisation of string.

    Args:
        text (_str_): string to be tokenised
        locale (__icu.Locale_, optional): ICU locale to use in tokenisation. Defaults to _icu.Locale.getRoot().

    Returns:
        _list_: list of graphemes
    """
gr = graphemes

####################
#
# ustr (ustring):
#   Class for unicode compliant string operations.
#
####################
class ustr(_UserString):
    def __init__(self, string):
        self._initial = string
        self._locale = None
        self._nform = None
        # self._unicodestring = _icu.UnicodeString(string)
        # self._graphemes = graphemes(string)
        self.debug = False
        super().__init__(string)

    def __str__(self):
        return self.data

    def __repr__(self):
        # return f'uString({self.data}, {self._initial}, {self._nform})'
        class_name = type(self).__name__
        limit = 100
        truncated: str = f'{"".join(graphemes(self.data)[0:round(2*limit/3)])}…' if len(self.data) > limit else self.data
        transformed: bool = True if self.data != self._initial else False
        return f"{class_name}(nform={self._nform}, locale={self._locale}, transformed={transformed}, string={truncated})"

    def _isbicameral(self):
        # Garay (Gara) to be added in Unicode v16
        # Zaghawa (Beria Giray Erfe) not in Unicode, preliminary proposal available, no script code.
        bicameral_scripts = {'Adlam', 'Armenian', 'Cherokee', 'Coptic', 'Cyrillic', 'Deseret', 'Glagolitic', 'Greek', 'Old_Hungarian', 'Latin', 'Osage', 'Vithkuqi', 'Warang_Citi'}
        scripts_in_text = set()
        for char in self.data:
            scripts_in_text.add(_unicodedataplus.script(char))
        return True if bicameral_scripts & scripts_in_text else False

    def _adjusted_width(self, n:int)->int:
        data = self.data
        adjustment: int = len(data) - _wcswidth(data)
        return n + adjustment

    def _get_binary_property_value(self, property):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.hasBinaryProperty(char, property))
        return all(status)

    def _set_locale(self, locale = None):
        if locale:
            self._locale = locale
        elif self._locale:
            locale = self._locale
        else:
            self._locale = locale = "default"
        match locale:
            case "root":
                return _icu.Locale.getRoot()
            case "und":
                return _icu.Locale.getRoot()
            case "default":
                return _icu.Locale.getDefault()
            case _  :
                return _icu.Locale(locale)

    def _set_parameters(self, new_data=None):
        if new_data:
            self.data = new_data
        # self._unicodestring = _icu.UnicodeString(self.data)
        # self._graphemes = _regex.findall(r'\X', self.data)
        # self._graphemes = graphemes(self.data)

    def _version(self):
        """Package version and unicode versions used.

        Returns:
            tuple: Tuple contianing (VERSION, PYICU_VERSION, ICU_VERSION, ICU_UNICODE_VERSION, UD_VERSION)
        """
        return (VERSION, PYICU_VERSION, ICU_VERSION, ICU_UNICODE_VERSION, UD_VERSION)

    def available_locales(self):
        return list(_icu.Locale.getAvailableLocales().keys())

    def available_transforms(self):
        return list(_icu.Transliterator.getAvailableIDs())

    def canonical_equivalents(self, verbose=False):
        deprecated = _regex.compile(r'[\u0340\u0341]')
        # graphemes_list = gr(self.data)
        results = []
        results_cp = []
        for grapheme in graphemes(self.data):
            ci = _icu.CanonicalIterator(grapheme)
            equivalents = [char for char in ci if not _regex.search(deprecated, char)]
            equivalents_cp = [codepoints(chars, prefix=False) for chars in equivalents]
            results_cp.append((grapheme, equivalents_cp))
            results.append(equivalents)
        if verbose:
            return results_cp
        return results
        # https://stackoverflow.com/questions/3308102/how-to-extract-the-n-th-elements-from-a-list-of-tuples

    def capitalise(self, locale = "default"):
        loc = self._set_locale(locale)
        # data = self.data.split(maxsplit=1)
        # if len(data) == 1:
        #     self.data = f"{str(_icu.UnicodeString(data[0]).toTitle(loc))}"
        # else:
        #     self.data = f"{str(_icu.UnicodeString(data[0]).toTitle(loc))} {str(_icu.UnicodeString(data[1]).toLower(loc))}"
        self.data = toSentence(self.data, use_icu = True, loc = loc)
        self._set_parameters()
        return self

    capitalize = capitalise

    def casefold(self, turkic = False):
        # return str(_icu.UnicodeString(self.data).foldCase())
        # option = 1 if turkic else 0
        # self.data = str(_icu.UnicodeString(self.data).foldCase(option))
        self.data = toCasefold(self.data, use_icu = True, turkic = turkic)
        self._set_parameters()
        return self

    # Case-insensitive
    ci = casefold

    # Canonical case-insensitive
    def cci(self, turkic=False):
        self.data = toNFD(toCasefold(toNFD(self.data, use_icu=True), use_icu=True, turkic = turkic), use_icu=True)
        self._set_parameters()
        return self

    def center(self, width: int, fillchar:str = " ") -> str:
        data = self.data
        return data.center(self._adjusted_width(width, data), fillchar)

    centre = center

    def codepoints(self, prefix = False, extended = False):
        # if extended:
        #     return ' '.join(f"U+{ord(c):04X} ({c})" for c in self.data) if prefix else ' '.join(f"{ord(c):04X} ({c})" for c in self.data)
        # else:
        #     return ' '.join(f"U+{ord(c):04X}" for c in self.data) if prefix else ' '.join(f"{ord(c):04X}" for c in self.data)
        return codepoints(self.data, prefix = prefix, extended = extended)

    def count(self, sub, start=None, end=None, use__regex=False, overlapping=False):
        text = self.data
        if use__regex:
            pattern = f'(?=({sub}))' if overlapping else sub
            text = text[start:end] if not start and not end else text
            return len(_regex.findall(pattern, text))
        return text.count(sub, start, end)

    def dominant_direction(self):
        return dominant_strong_direction(self.data)

    def dominant_script(self, mode="individual"):
        return dominant_script(self.data, mode=mode)

    # encode - from UserString
    # endswith - from UserString

    def envelope(self, dir = "auto", mode = "isolate"):
        self.data = bidi_envelope(self.data, dir, mode)
        self._set_parameters()
        return self

    # expandtabs - from UserString
    # find - from UserString
    # format - from UserString
    # format_map - from UserString

    def first_strong(self):
        return first_strong(self.data)

    def fullwidth(self):
        # return _icu.Transliterator.createInstance('Halfwidth-Fullwidth').transliterate(self.data)
        self.data = _icu.Transliterator.createInstance('Halfwidth-Fullwidth').transliterate(self.data)
        self._set_parameters()
        return self

    def get_initial(self):
        return self._initial

    def get_string(self):
        return self.data

    def graphemes(self):
        return graphemes(self.data)

    def grapheme_length(self):
        return len(graphemes(self.data))

    def halfwidth(self):
        # return _icu.Transliterator.createInstance('Fullwidth-Halfwidth').transliterate(self.data)
        self.data = _icu.Transliterator.createInstance('Fullwidth-Halfwidth').transliterate(self.data)
        self._set_parameters()
        return self

    # index - from UserString

    def isalnum(self):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isalnum(char))
        return all(status)

    def isalpha_posix(self):
        # Determines whether the specified code point is a letter character.
        # True for general categories "L" (letters).
        # Same as java.lang.Character.isLetter().
        # Serves as a C/POSIX migration function.
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isalpha(char))
        return all(status)

    def isalpha(self):
        # Check if a code point has the Alphabetic Unicode property.
        # Same as u_hasBinaryProperty(c, UCHAR_ALPHABETIC). This is different from u_isalpha!
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isUAlphabetic(char))
        return all(status)

    def isascii(self):
        data = self.data
        return data.isascii()

    def isbase(self):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isbase(char))
        return all(status)

    def isbidi(self):
        return is_bidi(self.data)

    def isblank(self):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isblank(char))
        return all(status)

    def iscntrl(self):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.iscntrl(char))
        return all(status)

    # isdecimal - from UserString

    def isdefined(self):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isdefined(char))
        return all(status)

    def isdigit(self):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isdigit(char))
        return all(status)

    def isgraph(self):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isgraph(char))
        return all(status)

    def isidentifier(self):
        data = self.data
        return data.isidentifier()

    def islower_posix(self):
        # Determines whether the specified code point has the general category "Ll" (lowercase letter). 
        # This misses some characters that are also lowercase but have a different general category value. 
        # In order to include those, use UCHAR_LOWERCASE.
        # This is a C/POSIX migration function.
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.islower(char))
        return all(status)

    def islower(self):
        # Check if a code point has the Lowercase Unicode property. 
        # Same as u_hasBinaryProperty(c, UCHAR_LOWERCASE). This is different from _icu.Char.islower! 
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isULowercase(char))
        return all(status)

    def ismirrored(self):
        # Determines whether the code point has the Bidi_Mirrored property.
        # This property is set for characters that are commonly used in Right-To-Left contexts 
        # and need to be displayed with a "mirrored" glyph.
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isMirrored(char))
        return all(status)

    # isnumeric - from UserString

    def isprintable(self):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isprint(char))
        return all(status)

    def ispunct(self):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.ispunct(char))
        return all(status)

    def isscript(self , script:str , common:bool=False) -> bool:
        return isScript(self.text, script=script, common=common)

    def isspace_posix(self):
        # Determines if the specified character is a space character or not. 
        # Note: There are several ICU whitespace functions;
        # This is a C/POSIX migration function.
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isspace(char))
        return all(status)

    isspace = isspace_posix

    def istitle(self, locale = "default"):
        loc = self._set_locale(locale)
        if not self._isbicameral():
            return False
        words = self.data.split()
        words_status = []
        for word in words:
            words_status.append(True) if word == str(_icu.UnicodeString(word).toTitle(loc)) else words_status.append(False)
        return all(words_status)

    def isupper_posix(self):
        # Determines whether the specified code point has the general category "Lu" (uppercase letter).
        # This misses some characters that are also uppercase but have a different general category value. In order # to include those, use UCHAR_UPPERCASE.
        # This is a C/POSIX migration function.
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isupper(char))
        return all(status)

    def isupper(self):
        # Check if a code point has the Uppercase Unicode property.
        # Same as u_hasBinaryProperty(c, UCHAR_UPPERCASE). This is different from u_isupper!
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isUUppercase(char))
        return all(status)

    def iswhitespace(self):
        # Determines if the specified code point is a whitespace character according to Java/ICU. 
        # A character is considered to be a Java whitespace character if and only if it satisfies one of the following criteria:
        #     * It is a Unicode Separator character (categories "Z" = "Zs" or "Zl" or "Zp"), but is not also a non-breaking space (U+00A0 NBSP or U+2007 Figure Space or U+202F Narrow NBSP).
        #     * It is U+0009 HORIZONTAL TABULATION.
        #     * It is U+000A LINE FEED.
        #     * It is U+000B VERTICAL TABULATION.
        #     * It is U+000C FORM FEED.
        #     * It is U+000D CARRIAGE RETURN.
        #     * It is U+001C FILE SEPARATOR.
        #     * It is U+001D GROUP SEPARATOR.
        #     * It is U+001E RECORD SEPARATOR.
        #     * It is U+001F UNIT SEPARATOR.
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isWhitespace(char))
        return all(status)

    def iswhitespaceU(self):
        # Check if a code point has the White_Space Unicode property.
        # Same as u_hasBinaryProperty(c, UCHAR_WHITE_SPACE).
        # This is different from both u_isspace and u_isWhitespace!
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isUWhiteSpace(char))
        return all(status)

    def isxdigit(self):
        status = []
        for char in [char for char in self.data]:
            status.append(_icu.Char.isxdigit(char))
        return all(status)

    # join - from UserString

    def ljust(self, width: int, fillchar:str = " ") -> str:
        data = self.data
        return data.ljust(self._adjusted_width(width, data), fillchar)

    def lower(self, locale = "default"):
        # return str(_icu.UnicodeString(self.data).toLower(_icu.Locale(locale))) if locale else str(_icu.UnicodeString(self.data).toLower())
        loc = self._set_locale(locale)
        # self.data = str(_icu.UnicodeString(self.data).toLower(loc))
        self.data = toLower(self.data, True, loc)
        self._set_parameters()
        return self

    # TODO: add optional _regex support
    def lstrip(self, chars=None):
        data = self.data
        self._set_parameters(data.lstrip(chars))
        return self

    # def normalize(self, nform):
    #     self._nform = nform.upper()
    #     if self._nform == "NFC":
    #         self.data = _icu.Normalizer2.getNFCInstance().normalize(self.data)
    #     elif self._nform == "NFD":
    #          self.data = _icu.Normalizer2.getNFDInstance().normalize(self.data)
    #     self._unicodestring = _icu.UnicodeString(self.data)
    #     self._graphemes = _regex.findall(r'\X',self.data)
    #     return self

    # maketrans - from UserString

    def normalise(self, nform=None, use_icu=True):
        if nform:
            self._nform = nform.upper()
        elif self._nform:
            nform = self._nform
        else:
            self._nform = nform = "NFD"
        if use_icu:
            match nform:
                case 'NFC':
                    self.data = _icu.Normalizer2.getNFCInstance().normalize(self.data)
                case 'NFKC':
                    self.data = _icu.Normalizer2.getNFKCInstance().normalize(self.data)
                case 'NFKD':
                    self.data = _icu.Normalizer2.getNFKDInstance().normalize(self.data)
                case "NFKC_CASEFOLD":
                    self.data = _icu.Normalizer2.getNFKCCasefoldInstance().normalize(self.data)
                case _:
                    self.data = _icu.Normalizer2.getNFDInstance().normalize(self.data)
        else:
            if nform == "NFKC_CASEFOLD" or "NFKC_CF":
                self.data = _unicodedataplus.normalize("NFC", _unicodedataplus.normalize('NFKC', self.data).casefold())
            else:
                self.data = _unicodedataplus.normalize(nform, self.data)
        # self._unicodestring = _icu.UnicodeString(self.data)
        # self._graphemes = _regex.findall(r'\X',self.data)
        return self

    normalize = normalise

    # partition - from UserString
    # removeprefix - from UserString
    # removesuffix - from UserString

    def remove_stopwords(self, stopwords):
        filtered_tokens = [word for word in self.data.split() if not word in stopwords]
        self.data = ' '.join(filtered_tokens)
        self._set_parameters()
        return self

    # TODO: Add optional _regex support
    # str.replace(old, new[, count])
    # re.sub(pattern, repl, string, count=0, flags=0)
    def replace(self, old, new, count=-1, flags=0, use__regex=False):
        if count == -1 and use__regex == True:
            count = 0
        data = self.data
        if use__regex:
            result = _regex.sub(old, new, data, count, flags) if flags else _regex.sub(old, new, data, count)
        else:
            result = data.replace(old, new, count)
        self._set_parameters(result)
        return self

    def reset(self):
        self.data = self._initial
        self._set_parameters()

    # rfind - from UserString
    # rindex - from UserString

    def rjust(self, width: int, fillchar:str = " ") -> str:
        data = self.data
        return data.rjust(self._adjusted_width(width, data), fillchar)

    # rpartition - from UserString

    def rsplit(self, sep=None, maxsplit=-1, flags=0):
        text = self.data
        # Adapted from https://stackoverflow.com/questions/38953278/what-s-the-equivalent-of-rsplit-with-re-split
        if maxsplit == 0 or not _regex.search(sep, text):
            return [text]
        if maxsplit == -1:
            maxsplit = 0
        if not sep:
            sep = r'\p{whitespace}'
        prev = len(text)                             # Previous match value start position
        cnt = 0                                      # A match counter
        result = []                                  # Output list
        for m in reversed(list(_regex.finditer(sep, text, flags=flags))):
            result.append(text[m.end():prev])        # Append a match to resulting list
            prev = m.start()                         # Set previous match start position
            cnt += 1                                 # Increment counter
            if maxsplit > 0 and cnt >= maxsplit:     # Break out of for loop if maxsplit is greater than 0 and...
                break                                # ...match count is more or equals max split value
        result.append(text[:prev])                   # Append the text chunk from start
        return reversed(result)                      # Return reversed list```

    # TODO: add optional _regex support
    def rstrip(self, chars=None):
        data = self.data
        self._set_parameters(data.rstrip(chars))
        return self

    def split(self, sep=None, maxsplit=-1, flags=0):
        # Logic _regex.split and str.split reverse outputs for maxsplit values of -1 and 0,
        # This implementation uses _regex.split(), but uses the maxsplit logic of str.split()
        # in order to keep API compatible.
        # To get python interpretation of whitespace, use the pattern r'[\p{whitespace}\u001C\u001D\u001E\u001F]'
        if maxsplit == 0:
            return [self.data]
        if maxsplit == -1:
            maxsplit = 0
        if not sep:
            sep = r'\p{whitespace}'
        return _regex.split(sep, self.data, maxsplit, flags)

    # splitlines - from UserString
    # startswith - from UserString

    # TODO: add optional _regex support
    def strip(self, chars=None):
        data = self.data
        self._set_parameters(data.strip(chars))
        return self

    def swap(self, s1, s2, temp ='\U0010FFFD'):
        data = self.data
        result =  data.replace(s1, temp).replace(s2, s1).replace(temp, s2)
        self._set_parameters(result)
        return self

    # TODO: swapcase

    def title(self, locale = "default"):
        loc = self._set_locale(locale)
        # self.data = str(_icu.UnicodeString(self.data).toTitle(loc))
        self.data = toTitle(self.data, True, loc)
        self._set_parameters()
        return self

    def token_frequencies(self, mode="word", locale="default"):
        # Frequencies of character, grapheme, or word tokens in uString object
        loc = self._set_locale(locale)
        tokens = []
        data = self.data
        match mode:
            case "character":
                tokens = [c for c in data]
            case "grapheme":
                tokens = graphemes(data)
            case _:
                tokens = tokenise(data, locale=loc)
        counts = _Counter(tokens)
        return sorted(counts.items(), key=lambda item: (-item[1], item[0]))

    def tokenise(self, mode="word", locale="default", pattern=None):
        # Frequencies of character, grapheme, or word tokens in uString object
        loc = self._set_locale(locale)
        tokens = []
        data = self.data
        match mode:
            case "character":
                tokens = [c for c in data]
            case "grapheme":
                tokens = graphemes(data)
            case "_regex":
                tokens = _regex.findall(pattern, data)
            case _:
                tokens = tokenise(data, locale=loc)
        return tokens

    def transform(self, id_label: str | None, rules: str | None = None, reverse: bool = False) -> _Self:
        """Use _icu.Transliterator to 
        Example:
            s = eli.uString('नागार्जुन')
            (s.data, s.transform('Deva-Latn').data, s.transform('Latin-ASCII').data)
            # ('नागार्जुन', 'nāgārjuna', 'nagarjuna')
            # s.data -> 'नागार्जुन'
            # s.transform('Deva-Latn').data -> 'nāgārjuna'
            # At this point s.data = 'nāgārjuna', so
            # s.transform('Latin-ASCII').data -> 'nagarjuna'

        Args:
            id_label (str | None): ID label for an ICU transliterator. If using custom rules, set to None.
            rules (str | None, optional): Custom transliteration rules for _icu.Transliterator. Defaults to None.
            reverse (bool, optional): Set to True if the reverse transformation is required. Defaults to False.

        Returns:
            Self: The data stored in the uString object is updated to the transformed string. And Self returned for further methods.
        """
        direction = _icu.UTransDirection.REVERSE if reverse else _icu.UTransDirection.FORWARD
        if id_label is None and rules is None:
            return self
        if id_label in list(_icu.Transliterator.getAvailableIDs()):
            self.data = _icu.Transliterator.createInstance(id_label, direction).transliterate(self.data)
        if rules and id_label is None:
            self.data = _icu.Transliterator.createFromRules("custom", rules, direction).transliterate(self.data)
        self._set_parameters()
        return self

    # translate - from UserString

    def truncate(self, limit: int = 100, mode: str = "character") -> str:
        if mode == "grapheme":
            return f'{"".join(graphemes(self.data)[0: limit])}…' if len(self.data) > limit else "".join(graphemes(self.data))
        return f'{self.data[0:limit]}…' if len(self.data) > limit else self.data

    def udata(self):
        udata(self.data)

    def unicodestring(self):
        return _icu.UnicodeString(self.data)

    UnicodeString = unicodestring

    def upper(self, locale: str = "default") -> _Self:
        """Return a copy of the string with all the cased characters converted to uppercase.

        Args:
            locale (str, optional): Locale identifier. Defaults to "default".

        Returns:
            Self: Updated uString object, with data uppercased.
        """
        loc = self._set_locale(locale)
        # self.data = str(_icu.UnicodeString(self.data).toUpper(loc))
        self.data = toUpper(self.data, True, loc)
        self._set_parameters()
        return self

    # zfill - from UserString

#
# Currently unmodified functions from UserString:
# 
# zfill
# translate 
# swapcase
# startswith
# splitlines
# rpartition
# rindex
# rfind
# removesuffix
# removeprefix
# partition
# maketrans
# join
# isnumeric
# isdecimal
# index 
# format_map 
# format 
# find 
# expantabs 
# endswith 
# encode 


# TODO:
#  * replace
#  * isnumeric
#  * isdecimal
#  * swapcase

# Investigate if changes required:
#  * endswidth
#  * startswith
#  * removesuffix
#  * removeprefix


# 'capitalize', 'center', 'count', 'encode', 'endswith', 'expandtabs', 'find', 'format', 'format_map', 'index', 'isdecimal', 'isdigit', 'isnumeric', 'istitle', 'isupper', 'join', 'ljust', 'maketrans', 'partition', 'removeprefix', 'removesuffix', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit',  'splitlines', 'startswith', 'swapcase', 'translate', 'zfill'

# posibilities from _icu.UnicodeString - 
# * trim, 
# * toTitle, 
# * startswith/startsWith, 
# * # * reverse, 
# * length, 
# * endswith/endsWith, 
# * compareBetween, 
# * compare, 
# * caseCompareBetween, 
# * caseCompare

#
# Ethiopic specific support
#

def _rbnf(localeID: str, flag: int = _icu.URBNFRuleSetTag.NUMBERING_SYSTEM):
    if empty_or_none(localeID):
        raise ValueError('Require locale ID.')
    locale = _icu.Locale(localeID)
    f = _icu.RuleBasedNumberFormat(flag, locale)
    f.setDefaultRuleSet('%ethiopic')
    return f

def ethiopic_to_integer(number: int):
    if not isScript(number, 'Ethiopic') or not number.isnumeric():
        raise ValueError('Require Ethiopic numerals.')
    localeID = 'und-Ethi-u-nu-ethi'
    f = _rbnf(localeID = localeID)
    return f.parse(number).getInt64()

def integer_to_ethiopic(number: str):
    if not isinstance(number, int):
        raise ValueError('Require an integer')
    localeID = 'und-Ethi-u-nu-ethi'
    f = _rbnf(localeID = localeID)
    return f.format(number)

def ethiopian_to_datetime(ethiopian_dt, time_zone = None):
    pass

def datetime_to_ethiopian(date_time, time_zone = None):
    pass

def ethiopian_to_gregorian(ethiopian_dt, time_zone = None):
    pass

def gregorian_to_ethiopian(gregorian_dt, tz = None):
    pass

class EthiopicUstr(ustr):
    def __init__(self, string):
        self._initial = string
        self._localeID = None
        self._locale = None
        self._nform = None
        # self._unicodestring = _icu.UnicodeString(string)
        # self._graphemes = graphemes(string)
        self.debug = False
        super().__init__(string)

    def clean_punctuation(self):
        data = self.data
        self.data = data.replace('\u1361\u1361', '\u1362').replace('\u1361\u002D', '\u1366')
        self._set_parameters()
        return self

    def count_characters(self, localeID = None, use_dict = True):
        if empty_or_none(localeID):
            raise ValueError("Require a locale ID.")
        return count_characters(self.data, localeID=localeID, auxiliary=False, use_dict=use_dict)

    def count_ngrams(self, ngram_length = 2):
        return count_ngraphs(self.data, ngram_length = ngram_length)

    def from_integer(self, number = None):
        if not empty_or_none(number):
            return integer_to_ethiopic(number)
        return integer_to_ethiopic(self.data)

    def to_first_order(self):
        self.data = _Ethi(self.data).convert_order('ግዕዝ', as_string=True)
        self._set_parameters()
        return self

    def to_integer(self, number = None):
        if not empty_or_none(number):
            return ethiopic_to_integer(number)
        return ethiopic_to_integer(self.data)


