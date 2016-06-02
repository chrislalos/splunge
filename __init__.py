# import urllib.parse

import sys
import traceback
from splunge.Exceptions import GeneralClientEx
from splunge.Exceptions import InvalidMethodEx
from splunge.Exceptions import ModuleNotFoundEx
from splunge.PathString import PathString
from splunge import MagicLoader
from splunge.App import Application

__all__ = ['Application', 'MagicLoader']

