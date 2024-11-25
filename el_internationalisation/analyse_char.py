from tabulate import tabulate
import unicodedataplus as _unicodedataplus
# import el_internationalisation as eli
from .ustrings import cp

from collections import Counter as _Counter
import icu as _icu

def analyse_char(char: str, target: str = 'utf-8'):
    if len(char) > 1:
        print("anyalyse_char() only takes a single character as a string argument.")
        return None
    print(f'\n{char} – {cp(char, prefix=True)} – {_unicodedataplus.name(char) if _unicodedataplus.name(char) else ""}\n')
    table = []
    encodings = [
        'cp437', 'cp500', 'cp737', 'cp775', 'cp850',
        'cp852', 'cp855', 'cp856', 'cp857', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865',
        'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp1006', 'cp1026',
        'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257',
        'cp1258', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5',
        'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_13', 'iso8859_14',
        'iso8859_15', 'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2',
        'mac_roman', 'mac_turkish', 'ptcp154']

    for encoding in encodings:
        try:
            data = [encoding, char.encode('latin-1').hex(' '), char.encode('latin-1').decode(encoding), cp(char.encode('latin-1').decode(encoding))]
            table.append(data)
        except UnicodeEncodeError:
            data = [encoding, char.encode('latin-1').hex(' '), 'undef', 'undef']
        except UnicodeDecodeError:
            data = [encoding, char.encode('latin-1').hex(' '), 'undef', 'undef']
    print(tabulate(table, headers=["Encoding","Bytes as hex", "Bytes as chars"]))


# '\U0001F947'.encode('utf-8', 'surrogatepass').decode('utf-16')
# def analyse_hex(h):
#     # hex = 0xb0 or 'b0'
#     if isinstance(h, int):
#         h = hex(h)[2:]
#     if not isinstance(h, str):
#         pass
#     b = bytes.fromhex(h)
#     table = []
#     encodings = []


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






