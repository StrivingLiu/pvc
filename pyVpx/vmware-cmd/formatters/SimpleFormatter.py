from Formatter import Formatter, Register
from xml.sax.saxutils import quoteattr, escape

class SimpleFormatter(Formatter):

   def __init__(self, **kwargs):
      Formatter.__init__(self, listItemEnd='\n', **kwargs)

   def FormatField(self, key, value, width):
      fmt = '%-' + str(width + 4) + "s"
      if isinstance(value, basestring) and key != 'localPath':
         value = quoteattr(value)
      return fmt % value


Register(SimpleFormatter)
