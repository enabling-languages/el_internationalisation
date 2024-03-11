##########################################################
# el_strings
#
#   © Enabling Languages 2023
#   Released under the MIT License.
#
##########################################################

from collections import Counter, UserString
import icu
import prettytable
import regex
import unicodedataplus
from .bidi import bidi_envelope, is_bidi
from typing import Self
from functools import partial

# TODO:
#   * add type hinting
#   * add DocStrings

VERSION = "0.6.0"
UD_VERSION = unicodedataplus.unidata_version
ICU_VERSION = icu.ICU_VERSION
PYICU_VERSION = icu.VERSION
ICU_UNICODE_VERSION = icu.UNICODE_VERSION

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
    return "".join(["\u25CC" + i if unicodedataplus.combining(i) else i for i in list(text)])

# codepoints and characters in string
#
# Usage:
#    eli.codepoints("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪")
#    eli.cp("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪", extended=True)
#    eli.cp("𞤀𞤣𞤤𞤢𞤥 𞤆𞤵𞤤𞤢𞤪", prefix=True, extended=True)

def codepoints(text, prefix = False, extended = False):
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
    cplist = regex.split(", |,| ", codepoints)
    results = ""
    for c in cplist:
        results += chr(int(c, 16))
    return results
    # return "".join([chr(int(i.removeprefix('u+'), 16)) for i in regex.split(r'[,;]\s?|\s+', cps.lower())])

def canonical_equivalents_str(ustring):
    """List canonically equivalent strings for given string.

    Args:
        ustring (str): character, grapheme or short string to analyse.

    Returns:
        List[str]: list of all canonically equivalent forms of ustring.
    """
    ci =  icu.CanonicalIterator(ustring)
    return [' '.join(f"U+{ord(c):04X}" for c in char) for char in ci]

def canonical_equivalents(ci, ustring = None):
    """List canonically equivalent strings for given canonical iterator instance.

    Args:
        ci (icu.CanonicalIterator): a CanonicalIterator instance.

    Returns:
        List[str]: list of all canonically equivalent forms of ustring.
    """
    if ustring:
        ci.setSource(ustring)
    return [' '.join(f"U+{ord(c):04X}" for c in char) for char in ci]

def unicode_data(text, ce=False):
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
    if ce:
        print(canonical_equivalents_str(text))
    return None

udata = unicode_data

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
    isolates = bool(regex.search('[\u2066\u2067\u2068]', text)) and bool(regex.search('\u2069', text))
    embeddings = bool(regex.search('[\u202A\u202B]', text)) and bool(regex.search('\u202C', text))
    marks = bool(regex.search('[\u200E\u200F]', text))
    overrides = bool(regex.search('[\u202D\u202E]', text)) and bool(regex.search('\u202C', text))
    formating_characters = set(regex.findall('[\u200e\u200f\u202a-\u202e\u2066-\u2069]', text))
    formating_characters = {f"U+{ord(c):04X} ({unicodedataplus.name(c,'-')})" for c in formating_characters if formating_characters is not None}
    presentation_forms = has_presentation_forms(text)
    return (bidi_status, isolates, embeddings, marks, overrides, formating_characters, presentation_forms)

scan = scan_bidi

def first_strong(s):
    properties = ['ltr' if v == "L" else 'rtl' if v in ["AL", "R"] else "-" for v in [unicodedataplus.bidirectional(c) for c in list(s)]]
    for value in properties:
        if value == "ltr":
            return "ltr"
        elif value == "rtl":
            return "rtl"
    return None

def dominant_strong_direction(s):
    count = Counter([unicodedataplus.bidirectional(c) for c in list(s)])
    rtl_count = count['R'] + count['AL'] + count['RLE'] + count["RLI"]
    ltr_count = count['L'] + count['LRE'] + count["LRI"] 
    return "rtl" if rtl_count > ltr_count else "ltr"

def codepoint_names(text):
    return [f"U+{ord(c):04X} ({unicodedataplus.name(c,'-')})" for c in text]

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
    pattern = regex.compile(pattern_string)
    return bool(regex.match(pattern, text))

def dominant_script(text, mode="individual"):
    count = Counter([unicodedataplus.script(char) for char in text])
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
            gr = regex.findall(r'\X', self.text)
            c = {"".join(i for i in k): v for k, v in dict(Counter(tuple(gr)[idx : idx + self.size] for idx in range(len(gr) - 1))).items()}
        else:
            c = Counter(self.text[idx : idx + self.size] for idx in range(len(self.text) - 1))
        r = {x: count for x, count in c.items() if regex.match(pattern, x)} if self.filter else dict(c)
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
        # Convert data keys to list, i.e. list of ngraths
        return [i for i in self.data.keys()]

    def to_tuples(self):
        # Convert data dictionary to a list of tuples.
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
        return bool(regex.match(f'[{pattern}]', text))
    return bool(regex.match(f'^[{pattern}]*$', text))

####################
#
# Unicode normalisation
#   Simple wrappers for Unicode normalisation
#
####################

def register_transformation(id: str, rules: str, direction: int = icu.UTransDirection.FORWARD) -> None:
    """Register a custom transliterator, allowing it to be reused.

    Args:
        id (str): id for transliterator, to be used with icu.Transliterator.createInstance().
        rules (str): Transliteration/transformation rules. Refer to 
        direction (int, optional): Direction of transformation to be applied. Defaults to icu.UTransDirection.FORWARD.

    Returns:
        None:
    """
    if id not in list(icu.Transliterator.getAvailableIDs()):
        transformer = icu.Transliterator.createFromRules(id, rules, direction)
        icu.Transliterator.registerInstance(transformer)
    return None

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

def toCasefold(text, use_icu=False, turkic=False):
    if use_icu:
        option = 1 if turkic else 0
        return str(icu.UnicodeString(text).foldCase(option))
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
    return bool(regex.search(r'(^\p{Hangul}+$)', s))
def normalise_hangul(s, normalisation_form = "NFC"):
    if is_hangul(s):
        return unicodedataplus.normalize(normalisation_form, s)
    else:
        return s
def marc_hangul(text):
    return "".join(list(map(normalise_hangul, regex.split(r'(\P{Hangul})', text))))

def normalise(nf, text, use_icu=False):
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
        if bool(regex.search(r'\p{Hangul}', text)):
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
            transform_direction = icu.UTransDirection.FORWARD
            register_transformation(transform_id, nfm21_rules, transform_direction)
            transformer = icu.Transliterator.createInstance(transform_id, transform_direction)
            return transformer.transliterate(text)
        else:
            return marc21_normalise(text)
    elif nf == "NFKC_CF":
        if use_icu:
            normaliser = icu.Normalizer2.getNFKCCasefoldInstance()
        else:
            return toNFKC_Casefold(text)
    elif nf == "NFC" and use_icu:
        normaliser = icu.Normalizer2.getNFCInstance()
    elif nf == "NFKC" and use_icu:
        normaliser = icu.Normalizer2.getNFKCInstance()
    elif nf == "NFD" and use_icu:
        normaliser = icu.Normalizer2.getNFDInstance()
    elif nf == "NFKD" and use_icu:
        normaliser = icu.Normalizer2.getNFKDInstance()
    if use_icu:
        return normaliser.normalize(text)
    return unicodedataplus.normalize(nf, text)

####################
#
# Unicode matching
#
####################

# Simple matching
#   NFD(X) = NFD(Y)
def simple_match(x, y, use_icu=False):
    return toNFD(x, use_icu=use_icu) == toNFD(y, use_icu=use_icu)

# Cased matching
#   toLower(NFD(X)) = toLower(NFD(Y))
def cased_match(x, y, use_icu=False):
    return toNFD(x, use_icu=use_icu) == toNFD(y, use_icu=use_icu)

# Caseless matching
#   toCasefold(X) = toCasefold(Y)
def caseless_match(x, y, use_icu=False):
    return toCasefold(x, use_icu=use_icu) == toCasefold(y, use_icu=use_icu)

# Canonical caseless matching
#   NFD(toCasefold(NFD(X))) = NFD(toCasefold(NFD(Y)))
def canonical_caseless_match(x, y, use_icu=False):
    return toNFD(toCasefold(toNFD(x, use_icu=use_icu), use_icu=use_icu), use_icu=use_icu) == toNFD(toCasefold(toNFD(y, use_icu=use_icu), use_icu=use_icu), use_icu=use_icu)

# Compatibility caseless match
#   NFKD(toCasefold(NFKD(toCasefold(NFD(X))))) = NFKD(toCasefold(NFKD(toCasefold(NFD(Y)))))
def compatibility_caseless_match(x, y, use_icu=False):
    return toNFKD(toCasefold(toNFKD(toCasefold(toNFD(x, use_icu=use_icu), use_icu=use_icu), use_icu=use_icu), use_icu=use_icu), use_icu=use_icu) == toNFKD(toCasefold(toNFKD(toCasefold(toNFD(y, use_icu=use_icu), use_icu=use_icu), use_icu=use_icu), use_icu=use_icu), use_icu=use_icu)

# Identifier caseless match for a string Y if and only if: 
#   toNFKC_Casefold(NFD(X)) = toNFKC_Casefold(NFD(Y))`
def identifier_caseless_match(x, y, use_icu=False):
    return toNFKC_Casefold(toNFD(x, use_icu=use_icu), use_icu=use_icu) == toNFKC_Casefold(toNFD(y, use_icu=use_icu), use_icu=use_icu)


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

#
# TODO:
#   * migrate form engine flag to use_icu flag for consistency
#
def toSentence(s, engine="core", lang="und"):
    # loc = icu.Locale.forLanguageTag(lang)
    # lang = regex.split('[_\-]', lang.lower())[0]
    lang = regex.split(r'[_\-]', lang.lower())[0]
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
#     elif not use_icu and lang_subtag not in TURKIC:
#         return s.capitalize()
#     if lang_subtag not in list(icu.Locale.getAvailableLocales().keys()):
#         lang = "und"
#     loc = icu.Locale.getRoot() if lang == "und" else icu.Locale.forLanguageTag(lang)
#     result = str(icu.UnicodeString(s[0]).toUpper(loc)) + str(icu.UnicodeString(s[1:]).toLower(loc))
#     return result

#
# TODO:
#   * migrate form engine flag to use_icu flag for consistency
#
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
# tokenise():
#   Create a list of tokens in a string.
#
####################

def get_boundaries(text, bi):
    bi.setText(text)
    boundaries = [*bi]
    boundaries.insert(0, 0)
    return boundaries

def tokenise(text, locale=icu.Locale.getRoot(), mode="word"):
    """Tokenise a string: character, grapheme, word and sentense tokenisation supported.

    Args:
        text (_str_): string to tokenise.
        locale (_icu.Locale_, optional): icu.Locale to use for tokenisation. Defaults to icu.Locale.getRoot().
        mode (str, optional): Character, grapheme, word or sentense tokenisation to perform. Defaults to "word".

    Returns:
        _list_: list of tokens in string.
    """
    match mode.lower():
        case "character":
            return list(text)
        case "grapheme":
            bi = icu.BreakIterator.createCharacterInstance(locale)
        case "sentence":
            bi = icu.BreakIterator.createSentenceInstance(locale)
        case _:
            bi = icu.BreakIterator.createWordInstance(locale)
    boundary_indices = get_boundaries(text, bi)
    return [text[boundary_indices[i]:boundary_indices[i+1]] for i in range(len(boundary_indices)-1)]

tokenize = tokenise

####################
#
# graphemes():
#   Create a list of extended grapheme clusters in a string.
#
####################
# def graphemes(text):
#     return regex.findall(r'\X',text)

graphemes = partial(tokenise, mode="graphemes")
graphemes.__doc__ = """Grapheme tokenisation of string.

    Args:
        text (_str_): string to be tokenised
        locale (_icu.Locale_, optional): ICU locale to use in tokenisation. Defaults to icu.Locale.getRoot().

    Returns:
        _list_: list of graphemes
    """
gr = graphemes

####################
#
# ustring:
#   Class for unicode compliant string operations.
#
####################
class uString(UserString):
    def __init__(self, string):
        self._initial = string
        self._locale = None
        self._nform = None
        self._unicodestring = icu.UnicodeString(string)
        self._graphemes = graphemes(string)
        self.debug = False
        super().__init__(string)

    def __str__(self):
        return self.data

    def __repr__(self):
        # return f'uString({self.data}, {self._initial}, {self._nform})'
        class_name = type(self).__name__
        return f"{class_name}(nform={self._nform})"

    def _isbicameral(self):
        # Garay (Gara) to be added in Unicode v16
        # Zaghawa (Beria Giray Erfe) not in Unicode, preliminary proposal available, no script code.
        bicameral_scripts = {'Adlam', 'Armenian', 'Cherokee', 'Coptic', 'Cyrillic', 'Deseret', 'Glagolitic', 'Greek', 'Old_Hungarian', 'Latin', 'Osage', 'Vithkuqi', 'Warang_Citi'}
        scripts_in_text = set()
        for char in self.data:
            scripts_in_text.add(unicodedataplus.script(char))
        return True if bicameral_scripts & scripts_in_text else False

    def _get_binary_property_value(self, property):
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.hasBinaryProperty(char, property))
        return all(status)

    def _set_locale(self, locale = "default"):
        self._locale = locale
        match locale:
            case "root":
                return icu.Locale.getRoot()
            case "und":
                return icu.Locale.getRoot()
            case "default":
                return icu.Locale.getDefault()
            case _  :
                return icu.Locale(locale)

    def _set_parameters(self, new_data=None):
        if new_data:
            self.data = new_data
        self._unicodestring = icu.UnicodeString(self.data)
        # self._graphemes = regex.findall(r'\X', self.data)
        self._graphemes = graphemes(self.data)

    def available_locales(self):
        return list(icu.Locale.getAvailableLocales().keys())

    def available_transforms(self):
        return list(icu.Transliterator.getAvailableIDs())

    def canonical_equivalents(self, verbose=False):
        deprecated = regex.compile(r'[\u0340\u0341]')
        # graphemes_list = gr(self.data)
        results = []
        results_cp = []
        for grapheme in self._graphemes:
            ci = icu.CanonicalIterator(grapheme)
            equivalents = [char for char in ci if not regex.search(deprecated, char)]
            equivalents_cp = [codepoints(chars, prefix=False) for chars in equivalents]
            results_cp.append((grapheme, equivalents_cp))
            results.append(equivalents)
        if verbose:
            return results_cp
        return results
        # https://stackoverflow.com/questions/3308102/how-to-extract-the-n-th-elements-from-a-list-of-tuples

    def capitalise(self, locale = "default"):
        loc = self._set_locale(locale)
        data = self.data.split(maxsplit=1)
        if len(data) == 1:
            self.data = f"{str(icu.UnicodeString(data[0]).toTitle(loc))}"
        else:
            self.data = f"{str(icu.UnicodeString(data[0]).toTitle(loc))} {str(icu.UnicodeString(data[1]).toLower(loc))}"
        self._set_parameters()
        return self

    capitalize = capitalise

    def casefold(self, turkic = False):
        # return str(icu.UnicodeString(self.data).foldCase())
        option = 1 if turkic else 0
        self.data = str(icu.UnicodeString(self.data).foldCase(option))
        self._set_parameters()
        return self

    # Case-insensitive
    ci = casefold

    # Canonical case-insensitive
    def cci(self, turkic=False):
        self.data = toNFD(toCasefold(toNFD(self.data, use_icu=True), use_icu=True, turkic = turkic), use_icu=True)
        self._set_parameters()
        return self

    # center - from UserString

    def codepoints(self, prefix = False, extended = False):
        if extended:
            return ' '.join(f"U+{ord(c):04X} ({c})" for c in self.data) if prefix else ' '.join(f"{ord(c):04X} ({c})" for c in self.data)
        else:
            return ' '.join(f"U+{ord(c):04X}" for c in self.data) if prefix else ' '.join(f"{ord(c):04X}" for c in self.data)

    # count - from UserString
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

    def fullwidth(self):
        # return icu.Transliterator.createInstance('Halfwidth-Fullwidth').transliterate(self.data)
        self.data = icu.Transliterator.createInstance('Halfwidth-Fullwidth').transliterate(self.data)
        self._set_parameters()
        return self

    def get_initial(self):
        return self._initial

    def get_string(self):
        return self.data

    def graphemes(self):
        return self._graphemes

    def grapheme_length(self):
        return len(self._graphemes)

    def halfwidth(self):
        # return icu.Transliterator.createInstance('Fullwidth-Halfwidth').transliterate(self.data)
        self.data = icu.Transliterator.createInstance('Fullwidth-Halfwidth').transliterate(self.data)
        self._set_parameters()
        return self

    # index - from UserString

    def isalnum(self):
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.isalnum(char))
        return all(status)

    def isalpha(self):
        # Determines whether the specified code point is a letter character.
        # True for general categories "L" (letters).
        # Same as java.lang.Character.isLetter().
        # Serves as a C/POSIX migration function.
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.isalpha(char))
        return all(status)

    def isalphaU(self):
        # Check if a code point has the Alphabetic Unicode property.
        # Same as u_hasBinaryProperty(c, UCHAR_ALPHABETIC). This is different from u_isalpha!
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.isUAlphabetic(char))
        return all(status)

    def isascii(self):
        data = self.data
        return data.isascii()

    # isdecimal - from UserString
    # isdigit - from UserString

    def isidentifier(self):
        data = self.data
        return data.isidentifier()

    def islower(self):
        # Determines whether the specified code point has the general category "Ll" (lowercase letter). 
        # This misses some characters that are also lowercase but have a different general category value. 
        # In order to include those, use UCHAR_LOWERCASE.
        # This is a C/POSIX migration function.
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.islower(char))
        return all(status)

    def islowerU(self):
        # Check if a code point has the Lowercase Unicode property. 
        # Same as u_hasBinaryProperty(c, UCHAR_LOWERCASE). This is different from icu.Char.islower! 
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.isULowercase(char))
        return all(status)

    def ismirrored(self):
        # Determines whether the code point has the Bidi_Mirrored property.
        # This property is set for characters that are commonly used in Right-To-Left contexts 
        # and need to be displayed with a "mirrored" glyph.
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.isMirrored(char))
        return all(status)

    # isnumeric - from UserString

    def isprintable(self):
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.isprint(char))
        return all(status)

    def isspace(self):
        # Determines if the specified character is a space character or not. 
        # Note: There are several ICU whitespace functions;
        # This is a C/POSIX migration function.
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.isspace(char))
        return all(status)

    def istitle(self, locale = "default"):
        loc = self._set_locale(locale)
        if not self._isbicameral():
            return False
        words = self.data.split()
        words_status = []
        for word in words:
            words_status.append(True) if word == str(icu.UnicodeString(word).toTitle(loc)) else words_status.append(False)
        return all(words_status)


    def isupper(self):
        # Determines whether the specified code point has the general category "Lu" (uppercase letter).
        # This misses some characters that are also uppercase but have a different general category value. In order # to include those, use UCHAR_UPPERCASE.
        # This is a C/POSIX migration function.
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.isupper(char))
        return all(status)

    def isupperU(self):
        # Check if a code point has the Uppercase Unicode property.
        # Same as u_hasBinaryProperty(c, UCHAR_UPPERCASE). This is different from u_isupper!
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.isUUppercase(char))
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
            status.append(icu.Char.isWhitespace(char))
        return all(status)

    def iswhitespaceU(self):
        # Check if a code point has the White_Space Unicode property.
        # Same as u_hasBinaryProperty(c, UCHAR_WHITE_SPACE).
        # This is different from both u_isspace and u_isWhitespace!
        status = []
        for char in [char for char in self.data]:
            status.append(icu.Char.isUWhiteSpace(char))
        return all(status)

    # join - from UserString
    # ljust - from UserString

    def lower(self, locale = "default"):
        # return str(icu.UnicodeString(self.data).toLower(icu.Locale(locale))) if locale else str(icu.UnicodeString(self.data).toLower())
        loc = self._set_locale(locale)
        self.data = str(icu.UnicodeString(self.data).toLower(loc))
        self._set_parameters()
        return self

    # TODO: add optional regex support
    def lstrip(self, chars=None):
        data = self.data
        self._set_parameters(data.lstrip(chars))
        return self

    # def normalize(self, nform):
    #     self._nform = nform.upper()
    #     if self._nform == "NFC":
    #         self.data = icu.Normalizer2.getNFCInstance().normalize(self.data)
    #     elif self._nform == "NFD":
    #          self.data = icu.Normalizer2.getNFDInstance().normalize(self.data)
    #     self._unicodestring = icu.UnicodeString(self.data)
    #     self._graphemes = regex.findall(r'\X',self.data)
    #     return self

    # maketrans - from UserString

    def normalise(self, nform="NFD", use_icu=True):
        self._nform = nform.upper()
        if use_icu:
            match nform:
                case 'NFC':
                    self.data = icu.Normalizer2.getNFCInstance().normalize(self.data)
                case 'NFKC':
                    self.data = icu.Normalizer2.getNFKCInstance().normalize(self.data)
                case 'NFKD':
                    self.data = icu.Normalizer2.getNFKDInstance().normalize(self.data)
                case "NFKC_CASEFOLD":
                    self.data = icu.Normalizer2.getNFKCCasefoldInstance().normalize(self.data)
                case _:
                    self.data = icu.Normalizer2.getNFDInstance().normalize(self.data)
        else:
            if nform == "NFKC_CASEFOLD" or "NFKC_CF":
                self.data = unicodedataplus.normalize("NFC", unicodedataplus.normalize('NFKC', self.data).casefold())
            else:
                self.data = unicodedataplus.normalize(nform, self.data)
        self._unicodestring = icu.UnicodeString(self.data)
        self._graphemes = regex.findall(r'\X',self.data)
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

    # TODO: Add optional regex support
    # str.replace(old, new[, count])
    # re.sub(pattern, repl, string, count=0, flags=0)
    def replace(self, old, new, count=-1, flags=0, use_regex=False):
        if count == -1 and use_regex == True:
            count = 0
        data = self.data
        if use_regex:
            result = regex.sub(old, new, data, count, flags) if flags else regex.sub(old, new, data, count)
        else:
            result = data.replace(old, new, count)
        self._set_parameters(result)
        return self

    def reset(self):
        self.data = self._initial
        self._set_parameters()

    # rfind - from UserString
    # rindex - from UserString
    # rjust - from UserString
    # rpartition - from UserString

    def rsplit(self, sep=None, maxsplit=-1, flags=0):
        text = self.data
        # Adapted from https://stackoverflow.com/questions/38953278/what-s-the-equivalent-of-rsplit-with-re-split
        if maxsplit == 0 or not regex.search(sep, text):
            return [text]
        if maxsplit == -1:
            maxsplit = 0
        if not sep:
            sep = r'\p{whitespace}'
        prev = len(text)                             # Previous match value start position
        cnt = 0                                      # A match counter
        result = []                                  # Output list
        for m in reversed(list(regex.finditer(sep, text, flags=flags))):
            result.append(text[m.end():prev])        # Append a match to resulting list
            prev = m.start()                         # Set previous match start position
            cnt += 1                                 # Increment counter
            if maxsplit > 0 and cnt >= maxsplit:     # Break out of for loop if maxsplit is greater than 0 and...
                break                                # ...match count is more or equals max split value
        result.append(text[:prev])                   # Append the text chunk from start
        return reversed(result)                      # Return reversed list```

    # TODO: add optional regex support
    def rstrip(self, chars=None):
        data = self.data
        self._set_parameters(data.rstrip(chars))
        return self

    def split(self, sep=None, maxsplit=-1, flags=0):
        # Logic regex.split and str.split reverse outputs for maxsplit values of -1 and 0,
        # This implementation uses regex.split(), but uses the maxsplit logic of str.split()
        # in order to keep API compatible.
        # To get python interpretation of whitespace, use the pattern r'[\p{whitespace}\u001C\u001D\u001E\u001F]'
        if maxsplit == 0:
            return [self.data]
        if maxsplit == -1:
            maxsplit = 0
        if not sep:
            sep = r'\p{whitespace}'
        return regex.split(sep, self.data, maxsplit, flags)

    # splitlines - from UserString
    # startswith - from UserString

    # TODO: add optional regex support
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
        self.data = str(icu.UnicodeString(self.data).toTitle(loc))
        self._set_parameters()
        return self

    def token_frequencies(self, mode="words", locale=icu.Locale.getRoot()):
        # Frequencies of character, grapheme, or word tokens in uString object
        tokens = []
        data = self.data
        match mode:
            case "characters":
                tokens = [c for c in data]
            case "graphemes":
                tokens = self._graphemes
            case _:
                tokens = tokenise(data, locale=locale)
        counts = Counter(tokens)
        return sorted(counts.items(), key=lambda item: (-item[1], item[0]))

    def transform(self, id_label, rules = None, reverse = False):
        direction = icu.UTransDirection.REVERSE if reverse else icu.UTransDirection.FORWARD
        if id_label is None and rules is None:
            return self
        if id_label in list(icu.Transliterator.getAvailableIDs()):
            self.data = icu.Transliterator.createInstance(id_label, direction).transliterate(self.data)
        if rules and id_label is None:
            self.data = icu.Transliterator.createFromRules("custom", rules, direction).transliterate(self.data)
        self._set_parameters()
        return self

    # translate - from UserString

    def unicodestring(self):
        return self._unicodestring

    def upper(self, locale: str = "default") -> Self:
        """Return a copy of the string with all the cased characters converted to uppercase.

        Args:
            locale (str, optional): Locale identifier. Defaults to "default".

        Returns:
            Self: Updated uString object, with data uppercased.
        """
        loc = self._set_locale(locale)
        self.data = str(icu.UnicodeString(self.data).toUpper(loc))
        self._set_parameters()
        return self

    # zfill - from UserString

# TODO: uString
#    * dominant script  (script code, script name)
#    * dominant direction
#    * is_bidi
#  , * script (script code, script name)
#    * script extension  (script code, script name)
#    * first_strong
#    * isnumeric
#    * isdecimal
#    * isbase  -> uString.isbase
#    * isblank  -> uString.isblank
#    * iscntrl  -> uString.iscntrl
#    * isdefined  -> uString.isdefined
#    * isdigit  -> uString.isdigit
#    * isgraph  -> uString.isgraph
#    * ispunct  -> uString.ispunct
#    * istitle  -> uString.istitle

# 'capitalize', 'center', 'count', 'encode', 'endswith', 'expandtabs', 'find', 'format', 'format_map', 'index', 'isdecimal', 'isdigit', 'isnumeric', 'istitle', 'isupper', 'join', 'ljust', 'maketrans', 'partition', 'removeprefix', 'removesuffix', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit',  'splitlines', 'startswith', 'swapcase', 'translate', 'zfill'

# icu.UnicodeString - trim, toTitle, startswith/startsWith, reverse, length, endswith/endsWith, compareBetween, compare, caseCompareBetween, caseCompare
