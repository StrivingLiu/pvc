from Formatter import Formatter, Register
from xml.sax.saxutils import quoteattr, escape

class HtmlFormatter(Formatter):

   def __init__(self, **kwargs):
      Formatter.__init__(self,
                         dataStart='<table>\n',
                         dataEnd='</table>\n',
                         listItemStart='   <tr>',
                         listItemEnd='</tr>\n',
                         **kwargs)
         
   def FormatField(self, key, value, width):
      return '<td>%s</td>' % escape(str(value))

Register(HtmlFormatter)
