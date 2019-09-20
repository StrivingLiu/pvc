#!/usr/bin/env python

"""
Tree display functions.
"""

"""
@file Tree.py

This file defines the function FormatAsTree.
"""

from pyVmomi import VmomiSupport

Node = VmomiSupport.Object

try:
   from cStringIO import StringIO
except ImportError:
   from StringIO import StringIO


def _GetLineChars(stack, useVt100LineDrawingChars):
   if len(stack) == 0: return ''

   strList = []
   space = '\x20'

   if useVt100LineDrawingChars:
      lineDrawingOn       = '\x0f\x1b\x28\x30'
      lineDrawingOff      = '\x1b\x28\x42'
      lowLeftCorner       = '\x6d\x71'
      midLeftCorner       = '\x74\x71'
      vertLine            = '\x78'
      strList.append(lineDrawingOn)
   else:
      lowLeftCorner       = '`-'
      midLeftCorner       = '|-'
      vertLine            = '|'

   def _append(list, s): list.append('%-3s' % s)

   for i, lastChild in enumerate(stack):
      if i < len(stack) - 1:
         if lastChild:  _append(strList, space)
         else:          _append(strList, vertLine)
      else:
         if lastChild:  _append(strList, lowLeftCorner)
         else:          _append(strList, midLeftCorner)

   if useVt100LineDrawingChars: strList.append(lineDrawingOff)

   return ''.join(strList)


def FormatAsTree(data,
                 labelFunc=None,
                 labelAttr=None,
                 childrenFunc=None,
                 childrenAttr=None,
                 useVt100LineDrawingChars=False):
   """
   Displays a tree using VT100 line drawing characters or (uglier)
   regular ASCII characters.
   """

   def _recurse(data, childrenFunc, stack):
      lineChars = _GetLineChars(stack, useVt100LineDrawingChars)

      label = None
      if labelAttr:
         label = getattr(data, labelAttr, None)
      if not label:
         label = labelFunc(data)
      if not label:
         raise ValueError('Must specify labelFunc or labelAttr')

      if childrenAttr:
         children = getattr(data, childrenAttr, [])
      elif childrenFunc:
         children = childrenFunc(data)
      else:
         raise ValueError('Must specify childrenFunc or childrenAttr')

      output.write('%s%s\n' % (lineChars, label))

      if children:
         for i, child in enumerate(children):
            lastChild = (i == len(children) - 1)
            _recurse(child, childrenFunc, stack = stack + [lastChild])


   output = StringIO()

   try:
      _recurse(data, childrenFunc, stack=[])
      return output.getvalue()
   finally:
      output.close()


def _Main():
   import sys

   useVt100LineDrawingChars = (len(sys.argv) > 1 and sys.argv[1] == '--vt100')

   outline = Node(label='1', children=[
      Node(label='1.1'),
      Node(label='1.2', children=[
         Node(label='1.2.1'),
         Node(label='1.2.2', children=[
            Node(label='1.2.2.1'),
         ]),
         Node(label='1.2.3'),
      ]),
      Node(label='1.3', children=[
         Node(label='1.3.1'),
         Node(label='1.3.2'),
      ]),
   ])

   tree = FormatAsTree(data=outline,
                       labelAttr='label',
                       childrenAttr='children',
                       useVt100LineDrawingChars=useVt100LineDrawingChars)
   print('%s' % tree)

   employeeData = Node(employeeName='Jacob', directReports=[
      Node(employeeName='Richard'),
      Node(employeeName='Ben', directReports=[
         Node(employeeName='Julia'),
         Node(employeeName='Tom', directReports=[
            Node(employeeName='Michael'),
         ]),
         Node(employeeName='Goodwin'),
      ]),
      Node(employeeName='John', directReports=[
         Node(employeeName='Sawyer'),
         Node(employeeName='Claire'),
      ]),
   ])

   tree = FormatAsTree(data=employeeData,
                       labelAttr='employeeName',
                       childrenAttr='directReports',
                       useVt100LineDrawingChars=useVt100LineDrawingChars)
   print('%s' % tree)


# Start program
if __name__ == "__main__":
    _Main()
