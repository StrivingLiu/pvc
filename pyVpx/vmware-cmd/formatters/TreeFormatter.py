import Tree
from Formatter import Formatter, Register
#from SimpleFormatter import SimpleFormatter
#from JsonFormatter import JsonFormatter
from Utils import rec_getattr


class TreeFormatter(Formatter):

   def __init__(self, groupByAttrs=['type'], *args, **kwargs):
      Formatter.__init__(self, *args, **kwargs)
      self.groupByAttrs = groupByAttrs

   def labelFunc(self, record):
      if self.attrs:
         return ', '.join([str(rec_getattr(record, attr)) for attr in self.attrs])
      else:
         return rec_getattr(record, self.columnsInfo[0][0])
         
   def Format(self, data):
      rootNode = Tree.Node(nodeLabel='['+'/'.join(self.groupByAttrs)+']',
                           children=[],
                           nodesDict={})

      for item in data:
         node = rootNode
         for groupByAttr in self.groupByAttrs:
            groupByValue = str(rec_getattr(item, groupByAttr))
            nodesDict = node.nodesDict
            oldNode = node
            node = nodesDict.get(groupByValue, None)
            if not node:
               node = Tree.Node(nodeLabel=groupByValue, children=[], nodesDict={})
               oldNode.nodesDict[groupByValue] = node
               oldNode.children.append(node)
            
         node.children.append(item)
            
      print Tree.FormatAsTree(data=rootNode,
                              labelAttr='nodeLabel',
                              labelFunc=self.labelFunc,
                              childrenAttr='children',
                              useVt100LineDrawingChars=True)
      return ''

   def FormatField(self, key, value, width):
      return '%s' % (str(value))


Register(TreeFormatter)

