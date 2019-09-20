from Formatter import Formatter, Register
from xml.sax.saxutils import quoteattr, escape

class XmlFormatter(Formatter):

   def __init__(self, **kwargs):
      Formatter.__init__(self,
                         dataStart='<?xml version="1.0" encoding="UTF-8"?>\n' +
                                   '<Data>\n',
                         dataEnd='</Data>\n')

   def FormatListItem(self, record):
      tagName = type(record).__name__
      return '    <%s %s />\n' % (tagName, self.Format(record))

   def FormatField(self, key, value, width):
      return '%s=%s ' % (key.replace('.', '_'), quoteattr(str(value)))


Register(XmlFormatter)
