from typing import List, Optional
import icu
from .ustrings import gr

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

def available_methods(clss: str, search_string: str | None = None, mode: str = "cli") -> List[str] | None:
    """List class methods for specified class that match a search string.

    Args:
        clss (str): Class name
        search_string (str | None, optional): substring to filter class methods. Defaults to None.
        mode (str, optional): If output is to terminal or is returned to calling function. Defaults to "cli".

    Returns:
        List[str] | None: List of methods available in a class that match query.
    """
    mode = "script" if mode.lower() != "cli" else "cli"
    methods: List[str] = []
    if search_string:
        methods = [item for item in list(dir(clss)) if search_string.lower() in item.lower()]
    else:
        methods = [item for item in list(dir(clss)) if not item.startswith("_")]
    if mode == "cli":
        print(methods)
        return None
    return methods

def character_requirements(languages: List[str], ngraphs: bool = False, keep_graphemes: bool = True, auxiliary: bool = False, basic_latin: bool = True) -> List[str]:
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
    collator = icu.Collator.createInstance(icu.Locale.getRoot())
    letters = []
    for language in languages:
        ld = icu.LocaleData(language)
        us = ld.getExemplarSet(icu.ULocaleDataExemplarSetType.ES_STANDARD)
        if auxiliary:
            us.addAll(ld.getExemplarSet(icu.ULocaleDataExemplarSetType.ES_AUXILIARY))
        if not basic_latin:
            us.removeAll(icu.UnicodeSet(r'\p{Ascii}'))
        letters = [*letters, *us]
    if not ngraphs:
        if keep_graphemes:
            letters = gr("".join(letters))
        else:
            letters = list("".join(letters))
    letters = sorted(list(set(letters)), key=collator.getSortKey)
    return letters

import wcwidth
def len_char_terminal(phrase):
    return tuple(map(wcwidth.wcwidth, phrase))
def len_string_terminal(phrase):
    return wcwidth.wcswidth(phrase)
def max_len_terminal(phrase_list):
    res = max(phrase_list, key=len_string_terminal)
    return len_string_terminal(res)

max_width = max_len_terminal

def find_char_index(character:str, ustring:str) -> Optional[int]:
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