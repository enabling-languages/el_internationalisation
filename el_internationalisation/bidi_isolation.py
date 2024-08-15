####################################################################################################
#
# Bidi isolation: bidiIsolate()
#    Enabling Languages Python port of unicodeBidi.ts: https://github.com/signalapp/Signal-Desktop/blob/ce0fb220411b97722e1e080c14faa65d23165784/ts/util/unicodeBidi.ts
#    Original code by Signal Messenger, LLC
#    Released under AGPL 3.0 license
#
####################################################################################################

import regex as _regex
import types as _types
# from el_internationalisation import rtl_hack
# from .bidi import rtl_hack

dir_formatting = _types.SimpleNamespace()

dir_formatting.LTR_ISOLATE: str = '\u2066'
dir_formatting.RTL_ISOLATE: str = '\u2067'
dir_formatting.FIRST_STRONG_ISOLATE: str = '\u2068'
dir_formatting.POP_DIRECTIONAL_ISOLATE: str = '\u2069'
dir_formatting.LTR_EMBEDDING: str = '\u202A'
dir_formatting.RTL_EMBEDDING: str = '\u202B'
dir_formatting.LTR_OVERRIDE: str = '\u202D'
dir_formatting.RTL_OVERRIDE: str = '\u202E'
dir_formatting.POP_DIRECTIONAL_FORMATTING: str = '\u202C'

formatting_chars: list[str] = [
    dir_formatting.LTR_ISOLATE, dir_formatting.RTL_ISOLATE, 
    dir_formatting.FIRST_STRONG_ISOLATE, dir_formatting.POP_DIRECTIONAL_ISOLATE,
    dir_formatting.LTR_EMBEDDING, dir_formatting.RTL_EMBEDDING,
    dir_formatting.LTR_OVERRIDE, dir_formatting.RTL_OVERRIDE,
    dir_formatting.POP_DIRECTIONAL_FORMATTING
]

start_isolate_embedding = [
  dir_formatting.LTR_ISOLATE, 
  dir_formatting.RTL_ISOLATE, 
  dir_formatting.FIRST_STRONG_ISOLATE]

other_start = [
  dir_formatting.LTR_EMBEDDING, dir_formatting.RTL_EMBEDDING,
  dir_formatting.LTR_OVERRIDE, dir_formatting.RTL_OVERRIDE
]

formatting_chars_pattern: str = rf'[{",".join(formatting_chars)}]'

def has_any_dir_format_chars(text: str) -> bool:
    return bool(_regex.search(formatting_chars_pattern, text))

# # U+061C ARABIC LETTER MARK
# ARABIC LETTER MARK = '\u061C'
# # U+200E LEFT-TO-RIGHT MARK
# LEFT_TO_RIGHT_MARK = '\u200E'
# # U+200F RIGHT-TO-LEFT MARK
# RIGHT_TO_LEFT+MARK = u'\u200F'

# solitary_chars_pattern: str = r'[\u061C\u200E\u200F]'

# def hasAnySolitaryDirFormatChars(text: str) -> bool:
#     return bool(_regex.search(solitary_chars_pattern, text))



# See:
#    * https://github.com/signalapp/Signal-Desktop/blob/ce0fb220411b97722e1e080c14faa65d23165784/ts/util/unicodeBidi.ts#L124
#    * https://github.com/whatwg/html/issues/10251
#
def balance_dir_format_chars(text: str) -> str:
    if not has_any_dir_format_chars(text):
        return text
    result = ''
    formattingDepth = 0
    isolateDepth = 0
    for i in range(len(text)):
        char = text[i]
        match char:
            case char if char in other_start:
                formattingDepth += 1
                result += char
            case dir_formatting.POP_DIRECTIONAL_FORMATTING:
                formattingDepth -= 1
                # skip if its closing formatting that was never opened
                if formattingDepth >= 0:
                    result += char
            case char if char in start_isolate_embedding:
                isolateDepth += 1
                result += char
            case dir_formatting.POP_DIRECTIONAL_ISOLATE:
                isolateDepth -= 1
                # 3 skip if its closing an isolate that was never opened
                if isolateDepth >= 0:
                    result += char
            case _:
                result += char
        #  Ensure everything is closed
        suffix: str = ''
        if formattingDepth > 0:
            suffix += dir_formatting.POP_DIRECTIONAL_FORMATTING * formattingDepth
        if isolateDepth > 0:
            suffix += dir_formatting.POP_DIRECTIONAL_ISOLATE * isolateDepth
    return result + suffix


balance_bidi = balance_dir_format_chars

# See:
#    * https://github.com/signalapp/Signal-Desktop/blob/ce0fb220411b97722e1e080c14faa65d23165784/ts/util/unicodeBidi.ts#L189
#    * https://github.com/whatwg/html/issues/10251
#
def bidi_isolate(text:str, direction: str = "auto", fribidi: bool = False) -> str:
    """Wrap string in direction formatting characters to set string in an isolation embedding.

    Args:
        text (str): String to process.
        direction (str, optional): Set overall direction of string. Values are rtl, ltr and auto. Defaults to "auto".
        fribidi (bool, optional): Convert form ordered to visual display for terminals and consoles that do not support UBA.

    Returns:
        str: String with isolation embedding
    """
    match direction:
        case "rtl":
            start_isolate = dir_formatting.RTL_ISOLATE
        case "ltr":
            start_isolate = dir_formatting.LTR_ISOLATE
        case _:
            start_isolate = dir_formatting.FIRST_STRONG_ISOLATE
    result = f'{start_isolate}{balance_dir_format_chars(text)}{dir_formatting.POP_DIRECTIONAL_ISOLATE}'
    # if fribidi:
    #     return rtl_hack(result, RTL)
    return result

isolate = bidi_isolate

# Examples
#
# isolate('hello')  -->  '\u2068hello\u2069'
# isolate('hello', direction="rtl")  -->  '\u2067hello\u2069'
# isolate('hello', direction="ltr")  -->  '\u2066hello\u2069'
# isolate('hello', direction="auto")  -->  '\u2068hello\u2069'
# isolate('\u202Ahello') --> '\u2068\u202Ahello\u202C\u2069'
# isolate('\u2069hello')  -->  '\u2068hello\u2069'


