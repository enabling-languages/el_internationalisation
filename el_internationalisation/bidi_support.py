import regex

def is_bidi(s):
    bidi_reg = r'[\p{bc=AL}\p{bc=AN}\p{bc=LRE}\p{bc=RLE}\p{bc=LRO}\p{bc=RLO}\p{bc=PDF}\p{bc=FSI}\p{bc=RLI}\p{bc=LRI}\p{bc=PDI}\p{bc=R}]'
    return bool(regex.search(bidi_reg, s))

isbidi = is_bidi

def bidi_envelope(s, dir="auto", mode="isolate"):
    mode = mode.lower()
    dir = dir.lower()
    if mode == "isolate":
        if dir == "rtl":
            s = "\u2067" + s + "\u2069"
        elif dir == "ltr":
            s = "\u2066" + s + "\u2069"
        elif dir == "auto":
            s = "\u2068" + s + "\u2069"
    elif mode == "embedding":
        if dir == "auto":
            dir = "rtl"
        if dir == "rtl":
            s = "\u202B" + s + "\u202C"
        elif dir == "ltr":
            s = "\u202A" + s + "\u202C"
    elif mode == "override":
        if dir == "auto":
            dir = "rtl"
        if dir == "rtl":
            s = "\u202E" + s + "\u202C"
        elif dir == "ltr":
            s = "\u202D" + s + "\u202C"
    return s

be = bidi_envelope

# strip bidi formatting characters
def strip_bidi(s):
    # U+2066..U+2069, U+202A..U+202E
    return regex.sub('[\u202a-\u202e\u2066-\u2069]', '', s)
