# This __all__ statement enables wildcard imports like: 'from locomotive import *'.
__all__ = ['app', 'capture', 'category_associations', 'classify', 'rss', 'news', 'recommend']

# system imports
import codecs
import locale
import sys

# application imports
import app
import capture
import category_associations
import classify
import news
import recommend
import rss

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
