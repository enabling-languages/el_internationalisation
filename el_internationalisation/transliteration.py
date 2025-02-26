import regex as _regex, icu as _icu, collections as _collections
import pathlib as _pathlib, sys as _sys
from .transliteration_data import SUPPORTED_TRANSLITERATORS, TRANSLIT_DATA
from .ustrings import normalise
import copy as _copy
import requests as _requests
import xml.etree.ElementTree as _ET

# TODO:
#  * add type hinting
#  * add DocStrings

DEFAULT_NF = "NFM21"

def toNFM21(text, engine="ud"):
    if engine.lower() == "_icu":
        return normalise("NFM21", text)
    return normalise("NFM21", text)

toNFM = toNFM21

def prep_string(s, dir, lang, bicameral = "latin-only", nf = DEFAULT_NF):
    # If both scripts are not bicameral, only lower case string if dirction
    # of Script-Latin is reverse. Ie Latin lowercase for conversion to
    # unicameral script.
    if dir.lower() == "reverse" and bicameral.lower() != "both":
        s = s.lower()
    # notmalise string to required form
    s = normalise(nf, s)
    # If converting from Latin to Lao (for ALALC), standarise 
    # interpretations of charcters used in ALALC Lao 2011 table.
    # LIkewise for Thai. Due to differences in interpretation due to
    # Removal of MARC-8 data during the 2011 revision of the 1997 tables.
    if (lang == "lo" or lang == "th") and dir.lower() == "reverse":
        s = s.replace("\u0327", "\u0328").replace("\u031C", "\u0328")
    return s

def el_transliterate(source, lang, dir = "forward", nf = DEFAULT_NF):
    lang = lang.replace("-", "_").split('_')[0]
    dir = dir.lower()
    if dir != "reverse":
        dir = "forward"
    if SUPPORTED_TRANSLITERATORS[lang]:
        translit_table = SUPPORTED_TRANSLITERATORS[lang]
        nf = nf.upper() if nf.upper() in ["NFC", "NFKC", "NFKC_CF", "NFD", "NFKD", "NFM"] else DEFAULT_NF
        source = prep_string(source, dir, lang, translit_table[1])
        if dir == "forward":
            collator = _icu.Collator.createInstance(_icu.Locale.getRoot())
        else:
            collator = _icu.Collator.createInstance(_icu.Locale(lang))
        if dir == "reverse" and lang in list(_icu.Collator.getAvailableLocales().keys()):
            collator = _icu.Collator.createInstance(_icu.Locale(lang))
        else:
            collator = _icu.Collator.createInstance(_icu.Locale.getRoot())
        word_dict = _collections.OrderedDict(sorted(TRANSLIT_DATA[translit_table[0]]['translit_dict'][dir].items(), reverse=True, key=lambda x: collator.getSortKey(x[0])))
        word_dict = {normalise(DEFAULT_NF, k): normalise(DEFAULT_NF, v) for k, v in word_dict.items()}
        label = translit_table[2]
        if dir == "reverse":
            source_split = _regex.split(r'(\W+?)', source)
            res = "".join(word_dict.get(ele, ele) for ele in source_split)
        else:
            from functools import reduce
            res = reduce(lambda x, y: x.replace(y, word_dict[y]), word_dict, source)
    else:
        res = source
    if nf != DEFAULT_NF:
        res = normalise(nf, res)
    return res

###############################################
#
# Athinkra Translit functions
#
###############################################

# Available transforms
def available_transforms(term = None):
    available = list(_icu.Transliterator.getAvailableIDs())
    if term is None:
        return available
    return [x for x in available if term.lower() in x.lower()]

# transliterate from inbuilt ICU transform
def translit__icu(source, transform):
    if transform not in available_transforms():
        print(f'Unsupported transformation. Not available in _icu4c {_icu.ICU_VERSION}')
        return
    transformer = _icu.Transliterator.createInstance(transform)
    if isinstance(source, list):
        return [transformer.transliterate(item) for item in source]
    return transformer.transliterate(source)

# READ transliteration rules from LDML file, either locale file path or URL
def read_ldml_rules(ldml_file):
    """Read transliteration rules from LDML file

    Args:
        ldml_file (str): Locale path or URL for LDML file containing transformation rules.

    Returns:
        tuple[str, str, str]: Tuple containing rules and forward and reverse labels.
    """
    def extract_rules(ldml_xml, rules_file):
        rules = ''
        r = ldml_xml.find('./supplementalData/transforms/transform')
        if r is None:
            r = ldml_xml.find('./transforms/transform')
        if r is None:
            _sys.stderr(f"Can't find transform in {rules_file}")
        pattern = _regex.compile(r'[ \t]{2,}|[ ]*#.+\n')
        rules = _regex.sub(pattern, '', r.find('./tRule').text)
        rules = _regex.sub('[\n#]', '', rules)
        rules_name = r.attrib['alias'].split()[0]
        reverse_name = ''
        # if r.attrib['backwardAlias']:
        if 'backwardAlias' in r.attrib:
            reverse_name = r.attrib['backwardAlias'].split()[0]
        return (rules, rules_name, reverse_name)

    def get_ldml(rules_file):
        if rules_file.startswith(('https://', 'http://')):
            r=_requests.get(rules_file)
            doc = _ET.ElementTree(_ET.fromstring(r.content.decode('UTF-8')))
        else:
            doc = _ET.parse(rules_file)
        return extract_rules(doc, rules_file)

    rules_tuple = get_ldml(ldml_file)
    return rules_tuple

# Register transformer form LDML file
def register_ldml(ldml_file):
    ldml_rules = read_ldml_rules(ldml_file)
    ldml_transformer = _icu.Transliterator.createFromRules(ldml_rules[1], ldml_rules[0], _icu.UTransDirection.FORWARD)
    _icu.Transliterator.registerInstance(ldml_transformer)
    if ldml_rules[2]:
        reverse_ldml_transformer = _icu.Transliterator.createFromRules(ldml_rules[2], ldml_rules[0], _icu.UTransDirection.REVERSE)
        _icu.Transliterator.registerInstance(reverse_ldml_transformer)

# transform from custom rules
def translit_rules(source, rules, direction = _icu.UTransDirection.FORWARD, name = "Custom"):
    """Text transformation (transliteration) using custom rules or LDML files.

    Args:
        source (str | list[str]): String or List of strings to be transformed.
        rules (str): Rules to use for transformation.
        direction (int, optional): Direction of transformation (forward or reverse). Defaults to _icu.UTransDirection.FORWARD.
        name (str, optional): Label for transformation. Defaults to "Custom".

    Returns:
        str | list[str]: Transformed string or list.
    """
    transformer = _icu.Transliterator.createFromRules(name, rules, direction)
    if isinstance(source, list):
        return [transformer.transliterate(item) for item in source]
    return transformer.transliterate(source)

# Resolve LDML file path
def set_ldml_file_path(raw_path):
    """Resolve LDML file path.

    Args:
        raw_path (str): sting of relative or absolute path to LDML file.

    Returns:
        str: return a resolved path as a string.
    """
    p = _pathlib.Path(raw_path)
    try:
        p = p.resolve(strict=True)
    except FileNotFoundError:
        print("LDML file not found.")
    if p.exists() and p.is_file():
        return str(p)
    else:
        print("LDML does not exist.")

# Get language subtag form a BCP-47 langauge tage or from a locale label
def get_lang_subtag(lang):
    subtags = lang.replace("-", "_").split('_')
    remainder = _copy.deepcopy(subtags)
    lang_subtag = subtags[0]
    remainder.pop(0)
    script_subtag = ""
    country_subtag = ""
    # if len(subtags) > 1:
    if 1 < len(subtags):
        if bool(_regex.match(r"^([A-Z][a-z]{3})$", subtags[1])):
            script_subtag = subtags[1]
            remainder.pop(0)
        elif bool(_regex.match(r"^([A-Z]{2})$", subtags[1])):
            country_subtag = subtags[1]
            remainder.pop(0)
    if 2 < len(subtags):
        if bool(_regex.match(r"^([A-Z]{2})$", subtags[2])):
            country_subtag = subtags[2]
            remainder.pop(0)
    remainder_str = "-".join(remainder) if len(remainder) > 0 else ""
    return (lang_subtag, script_subtag, country_subtag, remainder_str)

# transform using dictionary
def translit_dict(source, lang, dir = "forward", nf = DEFAULT_NF):
    lang = get_lang_subtag(lang)[0]
    dir = "forward" if dir.lower() != "reverse" else "reverse"
    if SUPPORTED_TRANSLITERATORS[lang]:
        translit_table = SUPPORTED_TRANSLITERATORS[lang]
        nf = nf.upper() if nf.upper() in ["NFC", "NFKC", "NFKC_CF", "NFD", "NFKD", "NFM21"] else DEFAULT_NF
        # source = prep_string(source, dir, lang, translit_table[1])
        # if dir == "forward":
        #     collator = _icu.Collator.createInstance(_icu.Locale.getRoot())
        # else:
        #     collator = _icu.Collator.createInstance(_icu.Locale(lang))
        # if dir == "reverse" and lang in list(_icu.Collator.getAvailableLocales().keys()):
        #     collator = _icu.Collator.createInstance(_icu.Locale(lang))
        # else:
        #     collator = _icu.Collator.createInstance(_icu.Locale.getRoot())
        if dir == "reverse" and lang in list(_icu.Collator.getAvailableLocales().keys()):
            collator = _icu.Collator.createInstance(_icu.Locale(lang))
        else:
            collator = _icu.Collator.createInstance(_icu.Locale.getRoot())
        word_dict = _collections.OrderedDict(sorted(TRANSLIT_DATA[translit_table[0]]['translit_dict'][dir].items(), reverse=True, key=lambda x: collator.getSortKey(x[0])))
        word_dict = {normalise(DEFAULT_NF, k): normalise(DEFAULT_NF, v) for k, v in word_dict.items()}
        label = translit_table[2]
        if dir == "reverse":
            source_split = _regex.split(r'(\W+?)', source)
            res = "".join(word_dict.get(ele, ele) for ele in source_split)
        else:
            from functools import reduce
            res = reduce(lambda x, y: x.replace(y, word_dict[y]), word_dict, source)
    else:
        res = source
    if nf != DEFAULT_NF:
        res = normalise(nf, res)
    return res

# el_transliterate = translit_dict

#
# 1. Use prep_string() or similar normalisation before transofrmations
# 2. 
#

###############################################
#
# EL Translit functions
#
###############################################

def to_ascii(text: str, latin_only: bool = True) -> str:
    """Convert text to Basic Latin characters only (i.e. equivalent to ASCII)

    Args:
        text (str): String to transform.
        latin_only (bool, optional): If True, only Latin text is converted to Basic Latin (ASCII) equivalents, else other scripts are transliterated to Latin, then converted to Basic Latin (ASCII). Defaults to True.

    Returns:
        str: Transformed string.
    """
    if latin_only:
        transliterator = _icu.Transliterator.createInstance('Latin-ASCII')
    else:
        transliterator = _icu.Transliterator.createInstance('Any-Latin; Latin-ASCII')
    return transliterator.transliterate(text)