import icu as _icu
from functools import partialmethod as _partialmethod
import html as _html
from rich.console import Console as _Console
from rich.table import Table as _Table, box as _box
from hexdump import hexdump as _hexdump

#
# Refer to
#   * https://unicode-org.github.io/icu/userguide/strings/properties.html
#   * https://util.unicode.org/UnicodeJsps/properties.html
#   * https://util.unicode.org/UnicodeJsps/properties.jsp

BINARY_PROPERTIES = frozenset([0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 36, 42, 43, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64])
ICU_VERSION = float('.'.join(_icu.ICU_VERSION.split('.')[0:2]))

class InvalidCharLengthException(Exception):
    "Raised when the method requires exactly one character, but additional characters were given."
    pass

def get_property(char: str, property: int, short_name: bool = False, max_ver: float | None = None) -> str | bool | None:
    """_summary_

    Args:
        char (str): Single character to be evaluated
        property (int): Unicode property to evaluate.
        short_name (bool, optional): Return abbreviation for property value.
            Only applies to non-binary properties. Defaults to False.
            Where _icu.UPropertyNameChoice.SHORT_PROPERTY_NAME is 0 and
            _icu.UPropertyNameChoice.LONG_PROPERTY_NAME is 1

        Examples:
            get_property('𞤀', _icu.UProperty.ALPHABETIC)
            get_property('𞤀', _icu.UProperty.BLOCK)
            get_property('𞤀', _icu.UProperty.SCRIPT)
            get_property('\U0001e900', 4106, True)
            get_property('𞤀', _icu.UProperty.GENERAL_CATEGORY)
            get_property('𞤀', _icu.UProperty.GENERAL_CATEGORY, True)

        Refer to:
            * https://unicode-org.github.io/_icu/userguide/strings/properties.html
            * https://unicode-org.github.io/_icu-docs/apidoc/released/_icu4c/uchar_8h.html
            * https://www.unicode.org/Public/UCD/latest/ucd/PropertyAliases.txt
            * https://www.unicode.org/reports/tr44/#Properties

    Returns:
        str | bool | None: Property value for the character
    """
    if len(char) != 1:
        print("Please specify a single character.")
        return None

    if property in BINARY_PROPERTIES:
        return _icu.Char.hasBinaryProperty(char, property)
    name_choice = 0 if short_name else 1
    value = _icu.Char.getIntPropertyValue(char, property)
    return _icu.Char.getPropertyValueName(property, value, name_choice)

class ucd():
    def __init__(self, char):
        self._char = char
        self._name = _icu.Char.charName(self._char)
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
            return _icu.Char.hasBinaryProperty(char, property)

        name_choice = 0 if short_name else 1
        value = _icu.Char.getIntPropertyValue(char, property)
        return _icu.Char.getPropertyValueName(property, value, name_choice)

    UNICODE_VERSION = _icu.UNICODE_VERSION

    def age(self):
        return _icu.Char.charAge(self._char)

    alphabetic = _partialmethod(_get_property, property = _icu.UProperty.ALPHABETIC, short_name = False)
    ascii_hex_digit = _partialmethod(_get_property, property = _icu.UProperty.ASCII_HEX_DIGIT, short_name = False)
    basic_emoji = _partialmethod(_get_property, property = _icu.UProperty.BASIC_EMOJI, short_name = False)
    bidi_class = _partialmethod(_get_property, property = _icu.UProperty.BIDI_CLASS, short_name = False)
    bidi_class_code = _partialmethod(_get_property, property = _icu.UProperty.BIDI_CLASS, short_name = True)
    bidi_control = _partialmethod(_get_property, property = _icu.UProperty.BIDI_CONTROL, short_name = False)
    bidi_mirrored = _partialmethod(_get_property, property = _icu.UProperty.BIDI_MIRRORED, short_name = False)

    def bidi_mirroring_glyph(self):
        result = _icu.Char.charMirror(self._char)
        if result != self._char:
            return result
        return None

    def bidi_paired_bracket(self):
        result = _icu.Char.getBidiPairedBracket(self._char)
        if result != self._char:
            return result
        return None

    bidi_paired_bracket_type = _partialmethod(_get_property, property = _icu.UProperty.BIDI_PAIRED_BRACKET_TYPE, short_name = False)
    bidi_paired_bracket_type_code = _partialmethod(_get_property, property = _icu.UProperty.BIDI_PAIRED_BRACKET_TYPE, short_name = True)
    block = _partialmethod(_get_property, property = _icu.UProperty.BLOCK, short_name = False)
    block_code = _partialmethod(_get_property, property = _icu.UProperty.BLOCK, short_name = True)
    # see combining_class for numeric equivalent
    canonical_combining_class = _partialmethod(_get_property, property = _icu.UProperty.CANONICAL_COMBINING_CLASS, short_name = False)
    canonical_combining_class_code = _partialmethod(_get_property, property = _icu.UProperty.CANONICAL_COMBINING_CLASS, short_name = True)

    def case_folding(self):
        return _icu.CaseMap.fold(self._char)

    case_ignorable = _partialmethod(_get_property, property = _icu.UProperty.CASE_IGNORABLE, short_name = False)
    case_sensitive = _partialmethod(_get_property, property = _icu.UProperty.CASE_SENSITIVE, short_name = False)
    cased = _partialmethod(_get_property, property = _icu.UProperty.CASED, short_name = False)
    changes_when_casefolded = _partialmethod(_get_property, property = _icu.UProperty.CHANGES_WHEN_CASEFOLDED, short_name = False)
    changes_when_casemapped = _partialmethod(_get_property, property = _icu.UProperty.CHANGES_WHEN_CASEMAPPED, short_name = False)
    changes_when_lowercased = _partialmethod(_get_property, property = _icu.UProperty.CHANGES_WHEN_LOWERCASED, short_name = False)
    changes_when_nfkc_casefolded = _partialmethod(_get_property, property = _icu.UProperty.CHANGES_WHEN_NFKC_CASEFOLDED, short_name = False)
    changes_when_titlecased = _partialmethod(_get_property, property = _icu.UProperty.CHANGES_WHEN_TITLECASED, short_name = False)
    changes_when_uppercased = _partialmethod(_get_property, property = _icu.UProperty.CHANGES_WHEN_UPPERCASED, short_name = False)

    def character(self):
        return self._char

    def codepoint(self, decimal=False) -> str:
        if decimal:
            return int(self._cp, 16)
        return self._cp

    def combining_class(self):
        # see canonical_combining_class, canonical_combining_class_code for alphabetic equivalent
        return _icu.Char.getCombiningClass(self._char)

    dash = _partialmethod(_get_property, property = _icu.UProperty.DASH, short_name = False)
    decomposition_type = _partialmethod(_get_property, property = _icu.UProperty.DECOMPOSITION_TYPE, short_name = False)
    default_ignorable_code_point = _partialmethod(_get_property, property = _icu.UProperty.DEFAULT_IGNORABLE_CODE_POINT, short_name = False)
    diacritic = _partialmethod(_get_property, property = _icu.UProperty.DIACRITIC, short_name = False)

    # digit same as digit_value
    def digit(self):
        value = _icu.Char.digit(self._char)
        return value if value != -1 else None

    def digit_value(self):
        value = _icu.Char.charDigitValue(self._char)
        return value if value != -1 else None

    # direction - same as bidi_class
    def direction(self):
        value = _icu.charDirection(self._char)
        return _icu.Char.getPropertyValueName(_icu.UProperty.BIDI_CLASS, value, _icu.UPropertyNameChoice.LONG_PROPERTY_NAME)

    # direction_code - same as bidi_class_code
    def direction_code(self):
        value = _icu.charDirection(self._char)
        return _icu.Char.getPropertyValueName(_icu.UProperty.BIDI_CLASS, value, _icu.UPropertyNameChoice.SHORT_PROPERTY_NAME)

    east_asian_width = _partialmethod(_get_property, property = _icu.UProperty.EAST_ASIAN_WIDTH, short_name = False)
    east_asian_width_code = _partialmethod(_get_property, property = _icu.UProperty.EAST_ASIAN_WIDTH, short_name = True)
    emoji = _partialmethod(_get_property, property = _icu.UProperty.EMOJI, short_name = False)
    emoji_component = _partialmethod(_get_property, property = _icu.UProperty.EMOJI_COMPONENT, short_name = False)
    emoji_keycap_sequence = _partialmethod(_get_property, property = _icu.UProperty.EMOJI_KEYCAP_SEQUENCE, short_name = False)
    emoji_modifier = _partialmethod(_get_property, property = _icu.UProperty.EMOJI_MODIFIER, short_name = False)
    emoji_modifier_base = _partialmethod(_get_property, property = _icu.UProperty.EMOJI_MODIFIER_BASE, short_name = False)
    emoji_presentation = _partialmethod(_get_property, property = _icu.UProperty.EMOJI_PRESENTATION, short_name = False)
    extended_pictographic = _partialmethod(_get_property, property = _icu.UProperty.EXTENDED_PICTOGRAPHIC, short_name = False)
    extender = _partialmethod(_get_property, property = _icu.UProperty.EXTENDER, short_name = False)

    def fc_nfkc_closure(self):
        return _icu.Char.getFC_NFKC_Closure(self._char)

    # def for_digit(self, radix=10):
    #     return _icu.Char.forDigit(int(self._char), radix)

    full_composition_exclusion = _partialmethod(_get_property, property = _icu.UProperty.FULL_COMPOSITION_EXCLUSION, short_name = False)
    general_category = _partialmethod(_get_property, property = _icu.UProperty.GENERAL_CATEGORY, short_name = False)
    general_category_code = _partialmethod(_get_property, property = _icu.UProperty.GENERAL_CATEGORY, short_name = True)
    general_category_mask = _partialmethod(_get_property, property = _icu.UProperty.GENERAL_CATEGORY_MASK, short_name = False)
    grapheme_base = _partialmethod(_get_property, property = _icu.UProperty.GRAPHEME_BASE, short_name = False)
    grapheme_cluster_break = _partialmethod(_get_property, property = _icu.UProperty.GRAPHEME_CLUSTER_BREAK, short_name = False)
    grapheme_extend = _partialmethod(_get_property, property = _icu.UProperty.GRAPHEME_EXTEND, short_name = False)
    grapheme_link = _partialmethod(_get_property, property = _icu.UProperty.GRAPHEME_LINK, short_name = False)
    hangul_syllable_type = _partialmethod(_get_property, property = _icu.UProperty.HANGUL_SYLLABLE_TYPE, short_name = False)
    hangul_syllable_type_code = _partialmethod(_get_property, property = _icu.UProperty.HANGUL_SYLLABLE_TYPE, short_name = True)
    hex_digit = _partialmethod(_get_property, property = _icu.UProperty.HEX_DIGIT, short_name = False)

    def html_entity(self, hexadecimal = True):
        if int(self._cp, 16) < 128:
            return _html.escape(self._char)
        if hexadecimal:
            return f'&#x{self._cp};'
        return f'&#{int(self._cp, 16)};'

    id_continue = _partialmethod(_get_property, property = _icu.UProperty.ID_CONTINUE, short_name = False)
    id_start = _partialmethod(_get_property, property = _icu.UProperty.ID_START, short_name = False)
    hyphen = _partialmethod(_get_property, property = _icu.UProperty.HYPHEN, short_name = False)
    ideographic = _partialmethod(_get_property, property = _icu.UProperty.IDEOGRAPHIC, short_name = False)
    ids_binary_operator = _partialmethod(_get_property, property = _icu.UProperty.IDS_BINARY_OPERATOR, short_name = False)
    ids_trinary_operator = _partialmethod(_get_property, property = _icu.UProperty.IDS_TRINARY_OPERATOR, short_name = False)

    def in_set(self, uset):
        return True if self._char in list(_icu.UnicodeSet(uset)) else False

    indic_positional_category = _partialmethod(_get_property, property = _icu.UProperty.INDIC_POSITIONAL_CATEGORY, short_name = False)
    indic_syllabic_category = _partialmethod(_get_property, property = _icu.UProperty.INDIC_SYLLABIC_CATEGORY, short_name = False)
    int_start = _partialmethod(_get_property, property = _icu.UProperty.INT_START, short_name = False)

    def is_alnum(self) -> bool:
        return _icu.Char.isalnum(self._char)

    def is_alpha(self) -> bool:
        return _icu.Char.isalpha(self._char)

    def is_ascii(self):
        char = self._char
        return char.isascii()

    def is_base(self) -> bool:
        return _icu.Char.isbase(self._char)

    def is_blank(self) -> bool:
        return _icu.Char.isblank(self._char)

    def is_cased(self) -> bool:
        # _icu.UProperty.CASED : 49
        return self._get_property(property = 49)

    def is_cntrl(self) -> bool:
        return _icu.Char.iscntrl(self._char)

    def is_defined(self) -> bool:
        return _icu.Char.isdefined(self._char)

    def is_digit(self) -> bool:
        return _icu.Char.isdigit(self._char)

    def is_graph(self) -> bool:
        return _icu.Char.isgraph(self._char)

    def is_id_ignorable(self):
        return _icu.Char.isIDIgnorable(self._char)

    def is_id_part(self):
        return _icu.Char.isIDPart(self._char)

    def is_id_start(self):
        return _icu.Char.isIDStart(self._char)

    def is_iso_control(self):
        return _icu.Char.isISOControl(self._char)

    def is_java_id_part(self):
        return _icu.Char.isJavaIDPart(self._char)

    def is_java_id_start(self):
        return _icu.Char.isJavaIDStart(self._char)

    def is_java_space_char(self):
        return _icu.Char.isJavaSpaceChar(self._char)

    def is_lower(self) -> bool:
        return _icu.Char.islower(self._char)

    def is_mirrored(self):
        return _icu.Char.isMirrored(self._char)

    def is_nfc(self):
        char = self._char
        norm_char = _icu.Normalizer2.getNFCInstance().normalize(char)
        return norm_char == char

    def is_nfkc(self):
        char = self._char
        norm_char = _icu.Normalizer2.getNFKCInstance().normalize(char)
        return norm_char == char

    def is_nfd(self):
        char = self._char
        norm_char = _icu.Normalizer2.getNFDInstance().normalize(char)
        return norm_char == char

    def is_nfkd(self):
        char = self._char
        norm_char = _icu.Normalizer2.getNFKDInstance().normalize(char)
        return norm_char == char

    def is_print(self):
        return _icu.Char.isprint(self._char)

    def is_punct(self):
        return _icu.Char.ispunct(self._char)

    def is_space(self):
        return _icu.Char.isspace(self._char)

    def is_script(self, sc:str) -> bool:
        return True if self.script() == sc or self.script_code == sc else False

    def is_title(self) -> bool:
        return _icu.Char.istitle(self._char)

    def is_u_alphabetic(self):
        return _icu.Char.isUAlphabetic(self._char)

    def is_u_lowercase(self):
        return _icu.Char.isULowercase(self._char)

    def is_u_uppercase(self):
        return _icu.Char.isUUppercase(self._char)

    def is_u_whitespace(self):
        return _icu.Char.isUWhiteSpace(self._char)

    def is_upper(self) -> bool:
        return _icu.Char.isupper(self._char)

    def is_whitespace(self):
        return _icu.Char.isWhitespace(self._char)

    def is_xdigit(self):
        return _icu.Char.isxdigit(self._char)
    join_control = _partialmethod(_get_property, property = _icu.UProperty.JOIN_CONTROL, short_name = False)
    joining_group = _partialmethod(_get_property, property = _icu.UProperty.JOINING_GROUP, short_name = False)
    joining_type = _partialmethod(_get_property, property = _icu.UProperty.JOINING_TYPE, short_name = False)
    lead_canonical_combining_class = _partialmethod(_get_property, property = _icu.UProperty.LEAD_CANONICAL_COMBINING_CLASS, short_name = False)
    line_break = _partialmethod(_get_property, property = _icu.UProperty.LINE_BREAK, short_name = False)
    logical_order_exception = _partialmethod(_get_property, property = _icu.UProperty.LOGICAL_ORDER_EXCEPTION, short_name = False)
    lowercase = _partialmethod(_get_property, property = _icu.UProperty.LOWERCASE, short_name = False)

    def lowercase_mapping(self):
        return _icu.CaseMap.toLower(self._char)

    mask_start = _partialmethod(_get_property, property = _icu.UProperty.MASK_START, short_name = False)
    math = _partialmethod(_get_property, property = _icu.UProperty.MATH, short_name = False)

    def mirror(self):
        return _icu.Char.charMirror(self._char)

    def name(self) -> str:
        return self._name

    def name_alias(self):
        return _icu.Char.charName(self._char, _icu.UCharNameChoice.CHAR_NAME_ALIAS)

    nfc_inert = _partialmethod(_get_property, property = _icu.UProperty.NFC_INERT, short_name = False)
    nfc_quick_check = _partialmethod(_get_property, property = _icu.UProperty.NFC_QUICK_CHECK, short_name = False)

    def nfd_contains(self, uset=_icu.UnicodeSet(r'[:Latin:]')) -> list[str]:
        normalizer = _icu.Normalizer2.getNFDInstance()
        domain = list(uset)
        return [item for item in domain if self._char in normalizer.normalize(item)]

    nfd_inert = _partialmethod(_get_property, property = _icu.UProperty.NFD_INERT, short_name = False)
    nfd_quick_check = _partialmethod(_get_property, property = _icu.UProperty.NFD_QUICK_CHECK, short_name = False)

    def nfkc_casefold(self):
        return _icu.Normalizer2.getNFKCCasefoldInstance().normalize(self._char)

    nfkc_inert = _partialmethod(_get_property, property = _icu.UProperty.NFKC_INERT, short_name = False)
    nfkc_quick_check = _partialmethod(_get_property, property = _icu.UProperty.NFKC_QUICK_CHECK, short_name = False)

    def nfkd_contains(self, uset=_icu.UnicodeSet(r'[:Latin:]')) -> list[str]:
        # _icu.ucd('b').nfkd_contains(_icu.UnicodeSet(r'[:Any:]'))
        normalizer = _icu.Normalizer2.getNFKDInstance()
        domain = list(uset)
        return [item for item in domain if self._char in normalizer.normalize(item)]

    nfkd_inert = _partialmethod(_get_property, property = _icu.UProperty.NFKD_INERT, short_name = False)
    nfkd_quick_check = _partialmethod(_get_property, property = _icu.UProperty.NFKD_QUICK_CHECK, short_name = False)
    noncharacter_code_point = _partialmethod(_get_property, property = _icu.UProperty.NONCHARACTER_CODE_POINT, short_name = False)
    numeric_type = _partialmethod(_get_property, property = _icu.UProperty.NUMERIC_TYPE, short_name = False)
    numeric_type_code = _partialmethod(_get_property, property = _icu.UProperty.NUMERIC_TYPE, short_name = True)

    def numeric_value(self):
        return _icu.Char.getNumericValue(self._char)

    pattern_syntax = _partialmethod(_get_property, property = _icu.UProperty.PATTERN_SYNTAX, short_name = False)
    pattern_white_space = _partialmethod(_get_property, property = _icu.UProperty.PATTERN_WHITE_SPACE, short_name = False)
    posix_alnum = _partialmethod(_get_property, property = _icu.UProperty.POSIX_ALNUM, short_name = False)
    posix_blank = _partialmethod(_get_property, property = _icu.UProperty.POSIX_BLANK, short_name = False)
    posix_graph = _partialmethod(_get_property, property = _icu.UProperty.POSIX_GRAPH, short_name = False)
    posix_print = _partialmethod(_get_property, property = _icu.UProperty.POSIX_PRINT, short_name = False)
    posix_xdigit = _partialmethod(_get_property, property = _icu.UProperty.POSIX_XDIGIT, short_name = False)
    prepended_concatenation_mark = _partialmethod(_get_property, property = _icu.UProperty.PREPENDED_CONCATENATION_MARK, short_name = False)
    quotation_mark = _partialmethod(_get_property, property = _icu.UProperty.QUOTATION_MARK, short_name = False)
    radical = _partialmethod(_get_property, property = _icu.UProperty.RADICAL, short_name = False)  # https://en.wikipedia.org/wiki/List_of_radicals_in_Unicode
    regional_indicator = _partialmethod(_get_property, property = _icu.UProperty.REGIONAL_INDICATOR, short_name = False)  # https://en.wikipedia.org/wiki/Regional_indicator_symbol
    # Move following to ucds()
    # rgi_emoji = _partialmethod(_get_property, property = _icu.UProperty.RGI_EMOJI, short_name = False)
    # rgi_emoji_flag_sequence = _partialmethod(_get_property, property = _icu.UProperty.RGI_EMOJI_FLAG_SEQUENCE, short_name = False)
    # rgi_emoji_modifier_sequence = _partialmethod(_get_property, property = _icu.UProperty.RGI_EMOJI_MODIFIER_SEQUENCE, short_name = False)
    # rgi_emoji_tag_sequence = _partialmethod(_get_property, property = _icu.UProperty.RGI_EMOJI_TAG_SEQUENCE, short_name = False)
    # rgi_emoji_zwj_sequence = _partialmethod(_get_property, property = _icu.UProperty.RGI_EMOJI_ZWJ_SEQUENCE, short_name = False)
    script = _partialmethod(_get_property, property = _icu.UProperty.SCRIPT, short_name = False)
    script_code = _partialmethod(_get_property, property = _icu.UProperty.SCRIPT, short_name = True)

    def script_extensions(self):
        return [_icu.Script(sc).getName() for sc in _icu.Script.getScriptExtensions(self._char)]

    def script_extensions_codes(self):
        return [_icu.Script(sc).getShortName() for sc in _icu.Script.getScriptExtensions(self._char)]

    segment_starter = _partialmethod(_get_property, property = _icu.UProperty.SEGMENT_STARTER, short_name = False)
    sentence_break = _partialmethod(_get_property, property = _icu.UProperty.SENTENCE_BREAK, short_name = False)

    def simple_case_folding(self):
        return _icu.Char.foldCase(self._char)
    def simple_lowercase_mapping(self):
        return _icu.Char.tolower(self._char)
    def simple_titlecase_mapping(self):
        return _icu.Char.totitle(self._char)
    def simple_uppercase_mapping(self):
        return _icu.Char.toupper(self._char)

    soft_dotted = _partialmethod(_get_property, property = _icu.UProperty.SOFT_DOTTED, short_name = False)
    s_term = _partialmethod(_get_property, property = _icu.UProperty.S_TERM, short_name = False)
    terminal_punctuation = _partialmethod(_get_property, property = _icu.UProperty.TERMINAL_PUNCTUATION, short_name = False)

    def titlecase_mapping(self):
        return _icu.CaseMap.toTitle(self._char)

    trail_canonical_combining_class = _partialmethod(_get_property, property = _icu.UProperty.TRAIL_CANONICAL_COMBINING_CLASS, short_name = False)

    # type same as general_category
    def type(self):
        value = _icu.Char.charType(self._char)
        _icu.Char.getPropertyValueName(_icu.UProperty.GENERAL_CATEGORY, value, _icu.UPropertyNameChoice.LONG_PROPERTY_NAME)

    # type_code same as general_category_code
    def type_code(self):
        value = _icu.Char.charType(self._char)
        _icu.Char.getPropertyValueName(_icu.UProperty.GENERAL_CATEGORY, value, _icu.UPropertyNameChoice.SHORT_PROPERTY_NAME)

    unified_ideograph = _partialmethod(_get_property, property = _icu.UProperty.UNIFIED_IDEOGRAPH, short_name = False)
    uppercase = _partialmethod(_get_property, property = _icu.UProperty.UPPERCASE, short_name = False)

    def uppercase_mapping(self):
        return _icu.CaseMap.toUpper(self._char)

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

    variation_selector = _partialmethod(_get_property, property = _icu.UProperty.VARIATION_SELECTOR, short_name = False)
    vertical_orientation = _partialmethod(_get_property, property = _icu.UProperty.VERTICAL_ORIENTATION, short_name = False)
    white_space = _partialmethod(_get_property, property = _icu.UProperty.WHITE_SPACE, short_name = False)
    word_break = _partialmethod(_get_property, property = _icu.UProperty.WORD_BREAK, short_name = False)
    xid_continue = _partialmethod(_get_property, property = _icu.UProperty.XID_CONTINUE, short_name = False)
    xid_start = _partialmethod(_get_property, property = _icu.UProperty.XID_START, short_name = False)

class ucd_str():
    def __init__(self, chars):
        self._chars = [ucd(char) for char in chars]
        self.data = [c.data for c in self._chars]

    def __str__(self):
        return "".join(self.characters())

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}(chars={self.characters()})"

    def ages(self):
        return [c.age() for c in self._chars]

    def blocks(self):
        return [c.block() for c in self._chars]

    def characters(self):
        return [c.character() for c in self._chars]

    def codepoints(self, decimal=False):
        return [c.codepoint(decimal) for c in self._chars]

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
    console = _Console()
    table = _Table(
        show_header=True,
        header_style="light_slate_blue",
        title="Character properties",
        box=_box.SQUARE, 
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

def casing_data(char: str):
    if len(char) > 1:
        raise(InvalidCharLengthException)
        print("Method takes a single character as a parameter.")
    char = ucd(char)
    upperc = (char.uppercase_mapping(), char.simple_uppercase_mapping())
    titlec = (char.titlecase_mapping(), char.simple_titlecase_mapping())
    lowerc = (char.lowercase_mapping(), char.simple_lowercase_mapping())
    cfolding = (char.case_folding(), char.simple_case_folding())
    console = _Console()
    table = _Table(
        show_header=True,
        header_style="light_slate_blue",
        title=f"Case mapping and folding",
        box=_box.SQUARE,
        caption=f"Character: {char.character()}")
    table.add_column("Operation")
    table.add_column("Full")
    table.add_column("Simple")
    table.add_row("Uppercase", upperc[0], upperc[1])
    table.add_row("Titlecase", titlec[0], titlec[1])
    table.add_row("Lowercase", lowerc[0], lowerc[1])
    table.add_row("Case folding", cfolding[0], cfolding[1])
    console.print(table)
    return None

def uset_to_list(notation:str) -> list[str]:
    uset = _icu.UnicodeSet(notation) 
    return list(uset)

def uset_to_pattern(notation: str) -> str:
    l = f'[{"".join(uset_to_list(notation))}]'
    return str(_icu.UnicodeSet(l).compact())

def uset_contains(chars:str, notation:str, mode:str='') -> bool:
    uset = _icu.UnicodeSet(notation)
    match mode.lower():
        case 'all':
            return uset.containsAll(chars)
        case "some":
            return uset.containsSome(chars)
        case "none":
            return uset.containsNone(chars)
        case _:
            return uset.contains(chars)

def count_unicode_for_method(fn) -> int:
    count = 0
    for i in range(0x10FFFF + 1):
        if fn(chr(i)):
            count += 1
    return count

def get_unicode_chars_for_method(fn, cp: bool = False) -> list[str]:
    chars = []
    for i in range(0x10FFFF + 1):
        if fn(chr(i)):
            chars.append(chr(i))
    if cp:
       return [f'{ord(ch):04X}' for ch in chars]
    return chars

def chars_to_codepoints(chars, decimal=False, enc='utf-8'):
    enc = enc.lower()
    result = []
    for char in chars:
        if ord(char) > 0xffff and enc == 'utf-16':
            result.extend(bytes(char, 'utf-16-be').hex(' ', bytes_per_sep=2).upper().split())
        else:
            result.append(f'{ord(char):04X}')
    if decimal:
        return [int(r, 16) for r in result]
    return result

# import el_internationalisation.data as elid
# s = 'abç 😊'
# elid.chars_to_codepoints(s)
# ['0061', '0062', '00E7', '0020', '1F60A']
# elid.chars_to_codepoints(s, True)
# [97, 98, 231, 32, 128522]
# elid.chars_to_codepoints(s, enc='utf-16')
# ['0061', '0062', '00E7', '0020', 'D83D', 'DE0A']
# elid.chars_to_codepoints(s, True, enc='utf-16')
# [97, 98, 231, 32, 55357, 56842]

def homogeneous_type(seq, typ):
    return all(isinstance(x, typ) for x in seq)
def codepoints_to_chars(codepoints, enc='utf-8'):
    enc = enc.lower()
    chars = [chr(c) for c in codepoints] if homogeneous_type(codepoints, int) else [chr(int(c, 16)) for c in codepoints]
    if enc == 'utf-16':
        return "".join(chars).encode('utf-16', 'surrogatepass').decode('utf-16')
    return "".join(chars)


# import el_internationalisation.data as elid
# elid.codepoints_to_chars(['0061', '0062', '00E7', '0020', '1F60A'])
# 'abç 😊'
# elid.codepoints_to_chars([97, 98, 231, 32, 128522])
# 'abç 😊'
# elid.codepoints_to_chars(['0061', '0062', '00E7', '0020', 'D83D', 'DE0A'], enc='utf-16')
# 'abç 😊'
# elid.codepoints_to_chars([97, 98, 231, 32, 55357, 56842], enc='utf-16')
# 'abç 😊'

def get_bytes(data, enc):
    byte_seq = []
    for char in data:
        try:
            byte_seq.append(char.encode(enc).hex(' ').upper())
        except UnicodeEncodeError:
            byte_seq.append('')
    return byte_seq

def display_byte_sequences(data: str, enc: str = 'utf-8') -> None:
    console = _Console()
    table = _Table(
        show_header=True,
        header_style="light_slate_blue",
        title="Byte representation of string",
        box=_box.SQUARE,
        caption=f"String: {data}\nEncoding: {enc}")
    table.add_column("Character")
    table.add_column("Bytes")
    byte_seq = get_bytes(data=data, enc=enc)
    for i, j in zip([*data], byte_seq):
        table.add_row(i, j)
    console.print(table)
    return None

# import el_internationalisation.data as elid
# elid.display_byte_sequences(input_chars, 'utf-8')
# elid.display_byte_sequences(input_chars, 'utf-16-be')
# elid.display_byte_sequences(input_chars, 'utf-32-be')
# elid.display_byte_sequences(input_chars, 'iso-8859-1')
# elid.display_byte_sequences(input_chars, 'iso-8859-19')
# elid.display_byte_sequences(input_chars, 'windows-1252')

def get_code_units(text: str, enc: str = 'utf-8', decimal: bool = False, structured=False) -> list[str|int|list[str|int]]:
    def is_structured(lst):
        return any(isinstance(i, list) for i in lst)
    if enc.lower() == 'utf-8':
        enc = enc.lower()
        bytes_per_sep = 1
    elif enc.lower() in ['utf-16', 'utf-16-be', 'utf-16-le']:
        enc = 'utf-16-be'
        bytes_per_sep = 2
    else:
        enc = 'utf-32-be'
        bytes_per_sep = 4
    if structured:
        result = [char.encode(enc).hex(' ', bytes_per_sep=bytes_per_sep).upper().split() for char in text]
    else:
        result = text.encode(enc).hex(' ', bytes_per_sep=bytes_per_sep).upper().split()
    if decimal:
        if is_structured(result):
            result = [[int(h, 16) for h in r] for r in result]
        else:
            result =  [int(r, 16) for r in result]
    return result

# import el_internationalisation.data as elid
# text = 'aéƒ'
# elid.get_code_units(text)
# ['61', 'c3', 'a9', 'c6', '92']
# elid.get_code_units(text, decimal=True)
# [97, 195, 169, 198, 146]
# elid.get_code_units(text, enc="utf-16")
# ['0061', '00e9', '0192']
# elid.get_code_units(text, enc="utf-16", decimal=True)
# [97, 233, 402]
# elid.get_code_units(text, enc="utf-32")
# ['00000061', '000000e9', '00000192']
# elid.get_code_units(text, enc="utf-32", decimal=True)
# [97, 233, 402]

def display_encoding_data(data, enc='utf-8', mode='codepoints_bytes'):
    match mode:
        case 'code_units':
            char_data = get_code_units(data, enc=enc, structured=True)
        case 'bytes':
            # char_data = [char.encode(enc).hex(' ').upper() for char in data]
            char_data = get_bytes(data=data, enc=enc)
        case _:
            char_data = [f'{ord(char):04X}' for char in data]
    console = _Console()
    table = _Table(
        show_header=False,
        title="Byte representation of string",
        box=_box.SQUARE,
        caption=f"String: {data}\nEncoding: {enc}",
        show_lines=True)
    for i in range(len(data)):
        table.add_column('', justify='center', vertical='middle')
    table.add_row(*data)
    table.add_row(*[" ".join(b) for b in char_data]) if mode == 'code_units' else table.add_row(*["".join(b) for b in char_data])
    if mode == 'codepoints_bytes':
        # byte_data = [char.encode(enc).hex(' ').upper() for char in data]
        byte_data = get_bytes(data=data, enc=enc)
        table.add_row(*["".join(b) for b in byte_data])
    console.print(table)
    return None

# import el_internationalisation.data as elid
# s = '€abç😊'
# elid.display_encoding_data(s)
# elid.display_encoding_data(s, mode='codepoints_bytes')
# elid.display_encoding_data(s, enc='windows-1252', mode='codepoints_bytes')
# elid.display_encoding_data(s, enc='latin-1', mode='codepoints_bytes')
# elid.display_encoding_data(s, mode='codepoints')
# elid.display_encoding_data(s, mode='code_units')
# elid.display_encoding_data(s, mode='bytes')

def analyse_bytes(data, encoding = 'utf-8'):
    if isinstance(data, str):
        data = data.encode(encoding)
    _hexdump(data)
