from Formatter import Formatter, Register
from xml.sax.saxutils import quoteattr, escape # Only used by XmlFormatter and JsonFormatter

class JsonFormatter(Formatter):

   def __init__(self, **kwargs):
      Formatter.__init__(self,
                         listStart='[\n',
                         listEnd='\n]\n',
                         listItemStart='   { ',
                         listItemEnd=' }',
                         listItemSep=',\n',
                         fieldSep=', ',
                         **kwargs)
         
   def FormatField(self, key, value, width):
      return '%s: %s' % (quoteattr(key.replace('.', '_')),
                         quoteattr(str(value)))


Register(JsonFormatter)
