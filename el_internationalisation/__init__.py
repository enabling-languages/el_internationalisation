"""
el_internationalisation

Helper functions to improve Python internationalization.
"""

__version__ = "0.1.1"
__author__ = 'Andrew Cunningham'
__credits__ = 'Enabling Languages'

from .digits import *
from .ustrings import *
from .bidi import *
from .analyse import *

del(digits)
del(ustrings)
del(bidi)
del(analyse)