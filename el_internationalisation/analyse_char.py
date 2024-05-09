from tabulate import tabulate
import unicodedataplus
import el_internationalisation as eli
from .ustrings import cp

def analyse_char(char: str, target: str = 'utf-8'):
    if len(char) > 1:
        print("anyalyse_char() only takes a single character as a string argument.")
        return None
    print(f'\n{char} – {cp(char, prefix=True)} – {unicodedataplus.name(char) if len(char) == 1 else ''}\n')
    table = []
    encodings = [
        'utf-8', 'utf-16-be', 'utf-16-le',
        'big5', 'big5hkscs', 'cp037', 'cp424', 'cp437', 'cp500', 'cp737', 'cp775', 'cp850',
        'cp852', 'cp855', 'cp856', 'cp857', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865',
        'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026',
        'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257',
        'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030',
        'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3',
        'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5',
        'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_13', 'iso8859_14',
        'iso8859_15', 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2',
        'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213']

    for encoding in encodings:
        try:
            data = [encoding, char.encode(encoding).hex(' '), char.encode(encoding).decode('raw_unicode_escape')]
            table.append(data)
        except UnicodeEncodeError:
            continue
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









