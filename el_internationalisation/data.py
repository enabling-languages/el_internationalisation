import icu
from functools import partialmethod
import html
from rich.console import Console
from rich.table import Table, box
from hexdump import hexdump

#
# Refer to
#   * https://unicode-org.github.io/icu/userguide/strings/properties.html
#   * https://util.unicode.org/UnicodeJsps/properties.html
#   * https://util.unicode.org/UnicodeJsps/properties.jsp

BINARY_PROPERTIES = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 36, 42, 43, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64]

def get_property(char: str, property: int, short_name: bool = False) -> str | bool | None:
    """_summary_

    Args:
        char (str): Single character to be evaluated
        property (int): Unicode property to evaluate.
        short_name (bool, optional): Return abbreviation for property value.
            Only applies to non-binary properties. Defaults to False.
            Where icu.UPropertyNameChoice.SHORT_PROPERTY_NAME is 0 and
            icu.UPropertyNameChoice.LONG_PROPERTY_NAME is 1

        Examples:
            get_property('𞤀', icu.UProperty.ALPHABETIC)
            get_property('𞤀', icu.UProperty.BLOCK)
            get_property('𞤀', icu.UProperty.SCRIPT)
            get_property('\U0001e900', 4106, True)
            get_property('𞤀', icu.UProperty.GENERAL_CATEGORY)
            get_property('𞤀', icu.UProperty.GENERAL_CATEGORY, True)

        Refer to:
            * https://unicode-org.github.io/icu/userguide/strings/properties.html
            * https://unicode-org.github.io/icu-docs/apidoc/released/icu4c/uchar_8h.html
            * https://www.unicode.org/Public/UCD/latest/ucd/PropertyAliases.txt
            * https://www.unicode.org/reports/tr44/#Properties

    Returns:
        str | bool | None: Property value for the character
    """
    if len(char) != 1:
        print("Please specify a single character.")
        return None

    if property in BINARY_PROPERTIES:
        return icu.Char.hasBinaryProperty(char, property)

    name_choice = 0 if short_name else 1
    value = icu.Char.getIntPropertyValue(char, property)
    return icu.Char.getPropertyValueName(property, value, name_choice)

class ucd():
    def __init__(self, char):
        self._char = char
        self._name = icu.Char.charName(self._char)
        self._cp = f'{ord(self._char):04X}'
        self.data = (
            self._char,
            self._cp,
            self._name,
            self.script(),
            self.block(),
            self.general_category_code(),
            self.bidi_class_code(),
            self.combining_class()
        )

    def __str__(self):
        return self._char

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}(char={self._char}, codepoint={self._cp}, name={self._name})"

    def _get_property(self, property: int, short_name: bool = False) -> str | bool:
        char = self._char
        if property in BINARY_PROPERTIES:
            return icu.Char.hasBinaryProperty(char, property)

        name_choice = 0 if short_name else 1
        value = icu.Char.getIntPropertyValue(char, property)
        return icu.Char.getPropertyValueName(property, value, name_choice)

    UNICODE_VERSION = icu.UNICODE_VERSION

    def age(self):
        return icu.Char.charAge(self._char)

    alphabetic = partialmethod(_get_property, property = icu.UProperty.ALPHABETIC, short_name = False)
    ascii_hex_digit = partialmethod(_get_property, property = icu.UProperty.ASCII_HEX_DIGIT, short_name = False)
    basic_emoji = partialmethod(_get_property, property = icu.UProperty.BASIC_EMOJI, short_name = False)
    bidi_class = partialmethod(_get_property, property = icu.UProperty.BIDI_CLASS, short_name = False)
    bidi_class_code = partialmethod(_get_property, property = icu.UProperty.BIDI_CLASS, short_name = True)
    bidi_control = partialmethod(_get_property, property = icu.UProperty.BIDI_CONTROL, short_name = False)
    bidi_mirrored = partialmethod(_get_property, property = icu.UProperty.BIDI_MIRRORED, short_name = False)

    def bidi_mirroring_glyph(self):
        result = icu.Char.charMirror(self._char)
        if result != self._char:
            return result
        return None

    def bidi_paired_bracket(self):
        result = icu.Char.getBidiPairedBracket(self._char)
        if result != self._char:
            return result
        return None

    bidi_paired_bracket_type = partialmethod(_get_property, property = icu.UProperty.BIDI_PAIRED_BRACKET_TYPE, short_name = False)
    bidi_paired_bracket_type_code = partialmethod(_get_property, property = icu.UProperty.BIDI_PAIRED_BRACKET_TYPE, short_name = True)
    block = partialmethod(_get_property, property = icu.UProperty.BLOCK, short_name = False)
    block_code = partialmethod(_get_property, property = icu.UProperty.BLOCK, short_name = True)
    # see combining_class for numeric equivalent
    canonical_combining_class = partialmethod(_get_property, property = icu.UProperty.CANONICAL_COMBINING_CLASS, short_name = False)
    canonical_combining_class_code = partialmethod(_get_property, property = icu.UProperty.CANONICAL_COMBINING_CLASS, short_name = True)

    def case_folding(self):
        return icu.CaseMap.fold(self._char)

    case_ignorable = partialmethod(_get_property, property = icu.UProperty.CASE_IGNORABLE, short_name = False)
    case_sensitive = partialmethod(_get_property, property = icu.UProperty.CASE_SENSITIVE, short_name = False)
    cased = partialmethod(_get_property, property = icu.UProperty.CASED, short_name = False)
    changes_when_casefolded = partialmethod(_get_property, property = icu.UProperty.CHANGES_WHEN_CASEFOLDED, short_name = False)
    changes_when_casemapped = partialmethod(_get_property, property = icu.UProperty.CHANGES_WHEN_CASEMAPPED, short_name = False)
    changes_when_lowercased = partialmethod(_get_property, property = icu.UProperty.CHANGES_WHEN_LOWERCASED, short_name = False)
    changes_when_nfkc_casefolded = partialmethod(_get_property, property = icu.UProperty.CHANGES_WHEN_NFKC_CASEFOLDED, short_name = False)
    changes_when_titlecased = partialmethod(_get_property, property = icu.UProperty.CHANGES_WHEN_TITLECASED, short_name = False)
    changes_when_uppercased = partialmethod(_get_property, property = icu.UProperty.CHANGES_WHEN_UPPERCASED, short_name = False)

    def character(self):
        return self._char

    def codepoint(self, decimal=False) -> str:
        if decimal:
            return int(self._cp, 16)
        return self._cp

    def combining_class(self):
        # see canonical_combining_class, canonical_combining_class_code for alphabetic equivalent
        return icu.Char.getCombiningClass(self._char)

    dash = partialmethod(_get_property, property = icu.UProperty.DASH, short_name = False)
    decomposition_type = partialmethod(_get_property, property = icu.UProperty.DECOMPOSITION_TYPE, short_name = False)
    default_ignorable_code_point = partialmethod(_get_property, property = icu.UProperty.DEFAULT_IGNORABLE_CODE_POINT, short_name = False)
    diacritic = partialmethod(_get_property, property = icu.UProperty.DIACRITIC, short_name = False)

    # digit same as digit_value
    def digit(self):
        value = icu.Char.digit(self._char)
        return value if value != -1 else None

    def digit_value(self):
        value = icu.Char.charDigitValue(self._char)
        return value if value != -1 else None

    # direction - same as bidi_class
    def direction(self):
        value = icu.charDirection(self._char)
        return icu.Char.getPropertyValueName(icu.UProperty.BIDI_CLASS, value, icu.UPropertyNameChoice.LONG_PROPERTY_NAME)

    # direction_code - same as bidi_class_code
    def direction_code(self):
        value = icu.charDirection(self._char)
        return icu.Char.getPropertyValueName(icu.UProperty.BIDI_CLASS, value, icu.UPropertyNameChoice.SHORT_PROPERTY_NAME)

    east_asian_width = partialmethod(_get_property, property = icu.UProperty.EAST_ASIAN_WIDTH, short_name = False)
    east_asian_width_code = partialmethod(_get_property, property = icu.UProperty.EAST_ASIAN_WIDTH, short_name = True)
    emoji = partialmethod(_get_property, property = icu.UProperty.EMOJI, short_name = False)
    emoji_component = partialmethod(_get_property, property = icu.UProperty.EMOJI_COMPONENT, short_name = False)
    emoji_keycap_sequence = partialmethod(_get_property, property = icu.UProperty.EMOJI_KEYCAP_SEQUENCE, short_name = False)
    emoji_modifier = partialmethod(_get_property, property = icu.UProperty.EMOJI_MODIFIER, short_name = False)
    emoji_modifier_base = partialmethod(_get_property, property = icu.UProperty.EMOJI_MODIFIER_BASE, short_name = False)
    emoji_presentation = partialmethod(_get_property, property = icu.UProperty.EMOJI_PRESENTATION, short_name = False)
    extended_pictographic = partialmethod(_get_property, property = icu.UProperty.EXTENDED_PICTOGRAPHIC, short_name = False)
    extender = partialmethod(_get_property, property = icu.UProperty.EXTENDER, short_name = False)

    def fc_nfkc_closure(self):
        return icu.Char.getFC_NFKC_Closure(self._char)

    # def for_digit(self, radix=10):
    #     return icu.Char.forDigit(int(self._char), radix)

    full_composition_exclusion = partialmethod(_get_property, property = icu.UProperty.FULL_COMPOSITION_EXCLUSION, short_name = False)
    general_category = partialmethod(_get_property, property = icu.UProperty.GENERAL_CATEGORY, short_name = False)
    general_category_code = partialmethod(_get_property, property = icu.UProperty.GENERAL_CATEGORY, short_name = True)
    general_category_mask = partialmethod(_get_property, property = icu.UProperty.GENERAL_CATEGORY_MASK, short_name = False)
    grapheme_base = partialmethod(_get_property, property = icu.UProperty.GRAPHEME_BASE, short_name = False)
    grapheme_cluster_break = partialmethod(_get_property, property = icu.UProperty.GRAPHEME_CLUSTER_BREAK, short_name = False)
    grapheme_extend = partialmethod(_get_property, property = icu.UProperty.GRAPHEME_EXTEND, short_name = False)
    grapheme_link = partialmethod(_get_property, property = icu.UProperty.GRAPHEME_LINK, short_name = False)
    hangul_syllable_type = partialmethod(_get_property, property = icu.UProperty.HANGUL_SYLLABLE_TYPE, short_name = False)
    hangul_syllable_type_code = partialmethod(_get_property, property = icu.UProperty.HANGUL_SYLLABLE_TYPE, short_name = True)
    hex_digit = partialmethod(_get_property, property = icu.UProperty.HEX_DIGIT, short_name = False)

    def html_entity(self, hexadecimal = True):
        if int(self._cp, 16) < 128:
            return html.escape(self._char)
        if hexadecimal:
            return f'&#x{self._cp};'
        return f'&#{int(self._cp, 16)};'

    id_continue = partialmethod(_get_property, property = icu.UProperty.ID_CONTINUE, short_name = False)
    id_start = partialmethod(_get_property, property = icu.UProperty.ID_START, short_name = False)
    hyphen = partialmethod(_get_property, property = icu.UProperty.HYPHEN, short_name = False)
    ideographic = partialmethod(_get_property, property = icu.UProperty.IDEOGRAPHIC, short_name = False)
    ids_binary_operator = partialmethod(_get_property, property = icu.UProperty.IDS_BINARY_OPERATOR, short_name = False)
    ids_trinary_operator = partialmethod(_get_property, property = icu.UProperty.IDS_TRINARY_OPERATOR, short_name = False)

    def in_set(self, uset):
        return True if self._char in list(icu.UnicodeSet(uset)) else False

    indic_positional_category = partialmethod(_get_property, property = icu.UProperty.INDIC_POSITIONAL_CATEGORY, short_name = False)
    indic_syllabic_category = partialmethod(_get_property, property = icu.UProperty.INDIC_SYLLABIC_CATEGORY, short_name = False)
    int_start = partialmethod(_get_property, property = icu.UProperty.INT_START, short_name = False)

    def is_alnum(self) -> bool:
        return icu.Char.isalnum(self._char)

    def is_alpha(self) -> bool:
        return icu.Char.isalpha(self._char)

    def is_ascii(self):
        char = self._char
        return char.isascii()

    def is_base(self) -> bool:
        return icu.Char.isbase(self._char)

    def is_blank(self) -> bool:
        return icu.Char.isblank(self._char)

    def is_cased(self) -> bool:
        # icu.UProperty.CASED : 49
        return self._get_property(property = 49)

    def is_cntrl(self) -> bool:
        return icu.Char.iscntrl(self._char)

    def is_defined(self) -> bool:
        return icu.Char.isdefined(self._char)

    def is_digit(self) -> bool:
        return icu.Char.isdigit(self._char)

    def is_graph(self) -> bool:
        return icu.Char.isgraph(self._char)

    def is_id_ignorable(self):
        return icu.Char.isIDIgnorable(self._char)

    def is_id_part(self):
        return icu.Char.isIDPart(self._char)

    def is_id_start(self):
        return icu.Char.isIDStart(self._char)

    def is_iso_control(self):
        return icu.Char.isISOControl(self._char)

    def is_java_id_part(self):
        return icu.Char.isJavaIDPart(self._char)

    def is_java_id_start(self):
        return icu.Char.isJavaIDStart(self._char)

    def is_java_space_char(self):
        return icu.Char.isJavaSpaceChar(self._char)

    def is_lower(self) -> bool:
        return icu.Char.islower(self._char)

    def is_mirrored(self):
        return icu.Char.isMirrored(self._char)

    def is_print(self):
        return icu.Char.isprint(self._char)

    def is_punct(self):
        return icu.Char.ispunct(self._char)

    def is_space(self):
        return icu.Char.isspace(self._char)

    def is_script(self, sc:str) -> bool:
        return True if self.script() == sc or self.script_code == sc else False

    def is_title(self) -> bool:
        return icu.Char.istitle(self._char)

    def is_u_alphabetic(self):
        return icu.Char.isUAlphabetic(self._char)

    def is_u_lowercase(self):
        return icu.Char.isULowercase(self._char)

    def is_u_uppercase(self):
        return icu.Char.isUUppercase(self._char)

    def is_u_whitespace(self):
        return icu.Char.isUWhiteSpace(self._char)

    def is_upper(self) -> bool:
        return icu.Char.isupper(self._char)

    def is_whitespace(self):
        return icu.Char.isWhitespace(self._char)

    def is_xdigit(self):
        return icu.Char.isxdigit(self._char)
    join_control = partialmethod(_get_property, property = icu.UProperty.JOIN_CONTROL, short_name = False)
    joining_group = partialmethod(_get_property, property = icu.UProperty.JOINING_GROUP, short_name = False)
    joining_type = partialmethod(_get_property, property = icu.UProperty.JOINING_TYPE, short_name = False)
    lead_canonical_combining_class = partialmethod(_get_property, property = icu.UProperty.LEAD_CANONICAL_COMBINING_CLASS, short_name = False)
    line_break = partialmethod(_get_property, property = icu.UProperty.LINE_BREAK, short_name = False)
    logical_order_exception = partialmethod(_get_property, property = icu.UProperty.LOGICAL_ORDER_EXCEPTION, short_name = False)
    lowercase = partialmethod(_get_property, property = icu.UProperty.LOWERCASE, short_name = False)

    def lowercase_mapping(self):
        return icu.CaseMap.toLower(self._char)

    mask_start = partialmethod(_get_property, property = icu.UProperty.MASK_START, short_name = False)
    math = partialmethod(_get_property, property = icu.UProperty.MATH, short_name = False)

    def mirror(self):
        return icu.Char.charMirror(self._char)

    def name(self) -> str:
        return self._name

    def name_alias(self):
        return icu.Char.charName(self._char, icu.UCharNameChoice.CHAR_NAME_ALIAS)

    nfc_inert = partialmethod(_get_property, property = icu.UProperty.NFC_INERT, short_name = False)
    nfc_quick_check = partialmethod(_get_property, property = icu.UProperty.NFC_QUICK_CHECK, short_name = False)
    nfd_inert = partialmethod(_get_property, property = icu.UProperty.NFD_INERT, short_name = False)
    nfd_quick_check = partialmethod(_get_property, property = icu.UProperty.NFD_QUICK_CHECK, short_name = False)

    def nfkc_casefold(self):
        return icu.Normalizer2.getNFKCCasefoldInstance().normalize(self._char)

    nfkc_inert = partialmethod(_get_property, property = icu.UProperty.NFKC_INERT, short_name = False)
    nfkc_quick_check = partialmethod(_get_property, property = icu.UProperty.NFKC_QUICK_CHECK, short_name = False)
    nfkd_inert = partialmethod(_get_property, property = icu.UProperty.NFKD_INERT, short_name = False)
    nfkd_quick_check = partialmethod(_get_property, property = icu.UProperty.NFKD_QUICK_CHECK, short_name = False)
    noncharacter_code_point = partialmethod(_get_property, property = icu.UProperty.NONCHARACTER_CODE_POINT, short_name = False)
    numeric_type = partialmethod(_get_property, property = icu.UProperty.NUMERIC_TYPE, short_name = False)
    numeric_type_code = partialmethod(_get_property, property = icu.UProperty.NUMERIC_TYPE, short_name = True)

    def numeric_value(self):
        return icu.Char.getNumericValue(self._char)

    pattern_syntax = partialmethod(_get_property, property = icu.UProperty.PATTERN_SYNTAX, short_name = False)
    pattern_white_space = partialmethod(_get_property, property = icu.UProperty.PATTERN_WHITE_SPACE, short_name = False)
    posix_alnum = partialmethod(_get_property, property = icu.UProperty.POSIX_ALNUM, short_name = False)
    posix_blank = partialmethod(_get_property, property = icu.UProperty.POSIX_BLANK, short_name = False)
    posix_graph = partialmethod(_get_property, property = icu.UProperty.POSIX_GRAPH, short_name = False)
    posix_print = partialmethod(_get_property, property = icu.UProperty.POSIX_PRINT, short_name = False)
    posix_xdigit = partialmethod(_get_property, property = icu.UProperty.POSIX_XDIGIT, short_name = False)
    prepended_concatenation_mark = partialmethod(_get_property, property = icu.UProperty.PREPENDED_CONCATENATION_MARK, short_name = False)
    quotation_mark = partialmethod(_get_property, property = icu.UProperty.QUOTATION_MARK, short_name = False)
    radical = partialmethod(_get_property, property = icu.UProperty.RADICAL, short_name = False)  # https://en.wikipedia.org/wiki/List_of_radicals_in_Unicode
    regional_indicator = partialmethod(_get_property, property = icu.UProperty.REGIONAL_INDICATOR, short_name = False)  # https://en.wikipedia.org/wiki/Regional_indicator_symbol
    # Move following to ucds()
    # rgi_emoji = partialmethod(_get_property, property = icu.UProperty.RGI_EMOJI, short_name = False)
    # rgi_emoji_flag_sequence = partialmethod(_get_property, property = icu.UProperty.RGI_EMOJI_FLAG_SEQUENCE, short_name = False)
    # rgi_emoji_modifier_sequence = partialmethod(_get_property, property = icu.UProperty.RGI_EMOJI_MODIFIER_SEQUENCE, short_name = False)
    # rgi_emoji_tag_sequence = partialmethod(_get_property, property = icu.UProperty.RGI_EMOJI_TAG_SEQUENCE, short_name = False)
    # rgi_emoji_zwj_sequence = partialmethod(_get_property, property = icu.UProperty.RGI_EMOJI_ZWJ_SEQUENCE, short_name = False)
    script = partialmethod(_get_property, property = icu.UProperty.SCRIPT, short_name = False)
    script_code = partialmethod(_get_property, property = icu.UProperty.SCRIPT, short_name = True)

    def script_extensions(self):
        return [icu.Script(sc).getName() for sc in icu.Script.getScriptExtensions(self._char)]

    def script_extensions_codes(self):
        return [icu.Script(sc).getShortName() for sc in icu.Script.getScriptExtensions(self._char)]

    segment_starter = partialmethod(_get_property, property = icu.UProperty.SEGMENT_STARTER, short_name = False)
    sentence_break = partialmethod(_get_property, property = icu.UProperty.SENTENCE_BREAK, short_name = False)

    def simple_case_folding(self):
        return icu.Char.foldCase(self._char)
    def simple_lowercase_mapping(self):
        return icu.Char.tolower(self._char)
    def simple_titlecase_mapping(self):
        return icu.Char.totitle(self._char)
    def simple_uppercase_mapping(self):
        return icu.Char.toupper(self._char)

    soft_dotted = partialmethod(_get_property, property = icu.UProperty.SOFT_DOTTED, short_name = False)
    s_term = partialmethod(_get_property, property = icu.UProperty.S_TERM, short_name = False)
    terminal_punctuation = partialmethod(_get_property, property = icu.UProperty.TERMINAL_PUNCTUATION, short_name = False)

    def titlecase_mapping(self):
        return icu.CaseMap.toTitle(self._char)

    trail_canonical_combining_class = partialmethod(_get_property, property = icu.UProperty.TRAIL_CANONICAL_COMBINING_CLASS, short_name = False)

    # type same as general_category
    def type(self):
        value = icu.Char.charType(self._char)
        icu.Char.getPropertyValueName(icu.UProperty.GENERAL_CATEGORY, value, icu.UPropertyNameChoice.LONG_PROPERTY_NAME)

    # type_code same as general_category_code
    def type_code(self):
        value = icu.Char.charType(self._char)
        icu.Char.getPropertyValueName(icu.UProperty.GENERAL_CATEGORY, value, icu.UPropertyNameChoice.SHORT_PROPERTY_NAME)

    unified_ideograph = partialmethod(_get_property, property = icu.UProperty.UNIFIED_IDEOGRAPH, short_name = False)
    uppercase = partialmethod(_get_property, property = icu.UProperty.UPPERCASE, short_name = False)

    def uppercase_mapping(self):
        return icu.CaseMap.toUpper(self._char)

    def utf8_bytes(self):
        char = self._char
        return char.encode('utf-8').hex(' ')

    def utf16_le_bytes(self):
        char = self._char
        return char.encode('utf-16-le').hex(' ')

    def utf16_be_bytes(self):
        char = self._char
        return char.encode('utf-16-be').hex(' ')

    def utf32_le_bytes(self):
        char = self._char
        return char.encode('utf-32-le').hex(' ')

    def utf32_be_bytes(self):
        char = self._char
        return char.encode('utf-32-be').hex(' ')

    variation_selector = partialmethod(_get_property, property = icu.UProperty.VARIATION_SELECTOR, short_name = False)
    vertical_orientation = partialmethod(_get_property, property = icu.UProperty.VERTICAL_ORIENTATION, short_name = False)
    white_space = partialmethod(_get_property, property = icu.UProperty.WHITE_SPACE, short_name = False)
    word_break = partialmethod(_get_property, property = icu.UProperty.WORD_BREAK, short_name = False)
    xid_continue = partialmethod(_get_property, property = icu.UProperty.XID_CONTINUE, short_name = False)
    xid_start = partialmethod(_get_property, property = icu.UProperty.XID_START, short_name = False)

class ucd_str():
    def __init__(self, chars):
        self._chars = [ucd(char) for char in chars]
        self.data = [c.data for c in self._chars]

    def __str__(self):
        return "".join(self.characters())

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}(chars={self.characters()})"

    def characters(self):
        return [c.character() for c in self._chars]

    def codepoints(self):
        return [c.codepoint() for c in self._chars]

    def in_set(self, uset):
        return [c.in_set(uset) for c in self._chars]

    def names(self):
        return [c.name() for c in self._chars]

    def scripts(self):
       return [c.script() for c in self._chars]

    def properties(self, property, short_name = False):
        return [c._get_property(property, short_name) for c in self._chars]

def unicode_data(text):
    """Display Unicode data for each character in string.

    Generate a table containing data on some Unicode character properties,
    including character codepoint and name, script character belongs to,

    Args:
        text (str): string to analyse.
    """
    data = ucd_str(text).data
    console = Console()
    table = Table(
        show_header=True,
        header_style="light_slate_blue",
        title="Character properties",
        box=box.SQUARE, 
        caption=f"String: {text}")
    table.add_column("char")
    table.add_column("cp")
    table.add_column("name")
    table.add_column("script")
    table.add_column("block")
    table.add_column("cat")
    table.add_column("bidi")
    table.add_column("cc")
    for datum in data:
        table.add_row(
            datum[0],
            datum[1],
            datum[2],
            datum[3],
            datum[4],
            datum[5],
            datum[6],
            str(datum[7]))
    # console.print(f"String: {text}")
    console.print(table)
    return None

udata = unicode_data


# def analyse_bytes(data, encoding = 'utf-8'):
#     if isinstance(data, str):
#         data = data.encode(encoding)
#     hexdump(data)

