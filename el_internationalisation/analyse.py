"""el_internationalisation: analyse characters

    Functions to assist in analysing Unicode strings, and assist in debugging encoding issues.

"""

import unicodedataplus, prettytable, regex
import icu
from .bidi import bidi_envelope, is_bidi
from .ustrings import has_presentation_forms
from collections import Counter

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

def unicode_data(text):
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
        pattern = f'[^\p\u007bP\u007d\p\u007bZ\u007d]\u007b{self.size}\u007d'
        r = {}
        if self.graphemes:
            gr = regex.findall(r'\X', self.text)
            c = {"".join(i for i in k): v for k, v in dict(Counter(tuple(gr)[idx : idx + 2] for idx in range(len(gr) - 1))).items()}
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
        return dict(list([self.data].items())[0: self.count])

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