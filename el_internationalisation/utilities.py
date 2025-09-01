from el_internationalisation import gr
import icu as _icu
import more_itertools as _mit
import requests as _requests
from typing import List as _List, Optional as _Optional
import wcwidth
import xml.etree.ElementTree as _ET

def list_to_string(items, sep = ', ', drop_bool = True):
    """Convert list to string

    Converts:
       ['one', 'two', 'three']
    to:
       'one, two, three'

    Args:
        items (list): _description_
        sep (str, optional): _description_. Defaults to ', '.

    Returns:
       str: _description_
    """
    # return sep.join([item for item in items if item])
    if not drop_bool:
        return sep.join(f'{item}' for item in items)
    return sep.join(f'{item}' for item in items if item)

def string_to_list(items, sep = ', '):
    """Convert string to list

    Converts:
       'one, two, three'
    to:
       ['one', 'two', 'three']

    Args:
        items (str): _description_
        sep (str, optional): _description_. Defaults to ', '.

    Returns:
        list: _description_
    """
    # return [item.strip() for item in items.split(sep) if item.strip()]
    return [item for item in items.split(sep) if item == item.strip() ]

def print_list(l, sep = "\n", drop_bool = True):
    """Print list to STDOUT

    Print list to STDOUT, using specified separator between list items, defaulting 
    to a new line.

    Args:
        l (list): _description_
        sep (str, optional): _description_. Defaults to "\n".
    """
    if sep == "\u0020":
        print(list_to_string(l, sep=sep, drop_bool=drop_bool))
    else:
        print(*l, sep=sep)

pl = print_list

def search_dict_values(dictionary, searchString):
    """Retrieve dictionary keys for matching values

    Args:
        dictionary (dict): _description_
        searchString (str): _description_

    Returns:
        list: _description_
    """
    return [key for key,val in dictionary.items() if any(searchString in s for s in val)]

def search_dict_keys(dictionary, searchString):
    """Retrieve dictionary values for matching keys

    Args:
        dictionary (dict): _description_
        searchString (str): _description_

    Returns:
        list: _description_
    """
    return dictionary[searchString] if dictionary.get(searchString) != None else None

def available_methods(clss: str, search_string: str | None = None, mode: str = "cli") -> _List[str] | None:
    """List class methods for specified class that match a search string.

    Args:
        clss (str): Class name
        search_string (str | None, optional): substring to filter class methods. Defaults to None.
        mode (str, optional): If output is to terminal or is returned to calling function. Defaults to "cli".

    Returns:
        List[str] | None: List of methods available in a class that match query.
    """
    mode = "script" if mode.lower() != "cli" else "cli"
    methods: _List[str] = []
    if search_string:
        methods = [item for item in list(dir(clss)) if search_string.lower() in item.lower()]
    else:
        methods = [item for item in list(dir(clss)) if not item.startswith("_")]
    if mode == "cli":
        print(methods)
        return None
    return methods

def character_requirements(languages: _List[str], ngraphs: bool = False, keep_graphemes: bool = True, auxiliary: bool = False, basic_latin: bool = True) -> _List[str]:
    """Generate a list of characters required for a language or locale.

    Uses CLDR locale data to identify characters required for a language or locale.
    Uses exemplar characters, but can optionally include auxiliary characters.

    Args:
        languages (List[str]): A list of languages or locales.
        ngraphs (bool, optional): Include (True) or segment(false) letters that are n-graphs. Defaults to False.
        auxiliary (bool, optional): Include exemplar characters. Defaults to False.
        basic_latin (bool, optional): Include (True) or exclude (False) letters from the Basic Latin block. Defaults to True.

    Returns:
        List[str]: _description_
    """
    collator = _icu.Collator.createInstance(_icu.Locale.getRoot())
    letters = []
    for language in languages:
        ld = _icu.LocaleData(language)
        us = ld.getExemplarSet(_icu.ULocaleDataExemplarSetType.ES_STANDARD)
        if auxiliary:
            us.addAll(ld.getExemplarSet(_icu.ULocaleDataExemplarSetType.ES_AUXILIARY))
        if not basic_latin:
            us.removeAll(_icu.UnicodeSet(r'\p{Ascii}'))
        letters = [*letters, *us]
    if not ngraphs:
        if keep_graphemes:
            letters = gr("".join(letters))
        else:
            letters = list("".join(letters))
    letters = sorted(list(set(letters)), key=collator.getSortKey)
    return letters

def len_char_terminal(phrase):
    return tuple(map(wcwidth.wcwidth, phrase))
def len_string_terminal(phrase):
    return wcwidth.wcswidth(phrase)
def max_len_terminal(phrase_list):
    res = max(phrase_list, key=len_string_terminal)
    return len_string_terminal(res)

max_width = max_len_terminal

def find_char_index(character:str, ustring:str) -> _Optional[int]:
    """Find index of the first occurrence of a character in string.

    Args:
        character (str): character to
        ustring (str): _description_

    Returns:
        Optional[int]: string index for character.
    """
    idx: int = ustring.find(character)
    if idx == -1:
        return None
    return idx

def expand_range(start_char: str = '', end_char: str = '', pattern: str = '') -> list[str]:
    """ Expand a range of characters or a UnicodeSet pattern into a list of characters.

    C.f generate_pattern()

    Args:
        start_char (str, optional): initial character in range. Defaults to ''.
        end_char (str, optional): final character in range. Defaults to ''.
        pattern (str, optional): _description_. Defaults to ''.

    Returns:
        list[str]: list of characters
    """    
    if pattern:
        return list(_icu.UnicodeSet(pattern))
    start_char = chr(start_char) if isinstance(start_char, int) else start_char
    end_char = chr(end_char) if isinstance(end_char, int) else end_char
    sequence = rf'[{start_char}-{end_char}]'
    return list(_icu.UnicodeSet(sequence))

def generate_pattern(sequence: list[str] | _icu.UnicodeSet) -> str:
    """ Generate a regex pattern from a list of characters or a UnicodeSet.

    C.f expand_range(), get_exemplars()

    Examples:
        >>> generate_pattern(['a', 'b', 'c', 'd', 'g', 'h', 'z'])
        '[a-dghz]'
        >>> uset = _icu.UnicodeSet("[a-dA-DgGhHzZ]")
        >>> generate_pattern(uset)
        '[A-DGHZa-dghz]'
        >>> generate_pattern(get_exemplars('de', use_sldr=True)['main'])
        '[a-zßäöü]'

    Args:
        sequence (list[str] | _icu.UnicodeSet): A list of characters or UnicodeSet

    Returns:
        str: A regex pattern representing the characters.
    """
    if isinstance(sequence, _icu.UnicodeSet):
        sequence = list(sequence)
    saved_groups = []
    for group in _mit.consecutive_groups(sequence, ord):
        saved_groups.append(list(group))  # Copy group elements
    iter_range = '['
    for group in saved_groups:
        if len(group) > 2:
            iter_range += f"{group[0]}-{group[-1]}"
        elif len(group) == 2:
            iter_range += f"{group[0]}{group[1]}"
        else:
            iter_range += f"{group[0]}"
    iter_range += ']'
    return iter_range

def get_exemplars(locale_id: str, use_sldr: bool = False) -> dict[str, str]:
    """Retrieve CLDR exemplar characters for a locale.

    Args:
        locale_id (str): A locale identifier, e.g. 'de', 'fr'
        use_sldr (bool, optional): Use SLDR data rather than CLDR data. Defaults to False.

    Returns:
        dict[str, str]: A dictionary of exemplar character sets.
    """    
    locale_id = locale_id.replace('-', '_')
    exemplar_data = dict()
    url = rf'https://raw.githubusercontent.com/unicode-org/cldr/main/common/main/{locale_id}.xml'
    if use_sldr:
        initial_letter = locale_id[0]
        url = rf'https://raw.githubusercontent.com/silnrsi/sldr/refs/heads/master/sldr/{initial_letter}/{locale_id}.xml'
    response = _requests.get(url)
    if response.status_code not in (404, 500):
        tree = _ET.fromstring(response.text)
        result = tree.findall('characters/exemplarCharacters')
        for element in result:
            type = element.attrib.get('type', 'main')
            if type not in ["numbers", "punctuation"]:
                if element.text and element.text != '↑↑↑':
                    exemplar_data[type] = _icu.UnicodeSet(rf'{element.text}')
        return exemplar_data
    return None

