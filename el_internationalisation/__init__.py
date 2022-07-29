"""
el_internationalisation

Helper functions to improve Python internationalization.
"""

__version__ = "0.1.1"
__author__ = 'Andrew Cunningham'
__credits__ = 'Enabling Languages'

from .digit_support import *
from .string_support import *
from .bidi_support import *
from .analyse import *

del(digit_support)
del(string_support)
del(bidi_support)
del(analyse)