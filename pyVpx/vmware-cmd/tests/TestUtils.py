#!/usr/bin/env python

"""
"""

import sys
try:
   from cStringIO import StringIO
except ImportError:
   from StringIO import StringIO


class RawInputStub(object):
   """
   Stub of raw_input that lets one specify what the answer will be
   instead of prompting the user.

   Example:

      >>> raw_input
      <built-in function raw_input>
      >>> rawInputStub = RawInputStub()
      >>> rawInputStub.answer = 'foobar'
      >>> value = raw_input('Enter a word')
      Enter a word
      >>> value
      'foobar'
      >>> rawInputStub.destroy()
      >>> raw_input
      <built-in function raw_input>
   """

   def __init__(self):
      self.old_raw_input = sys.modules['__builtin__'].raw_input
      sys.modules['__builtin__'].raw_input = self._raw_input

   def _raw_input(self, msg):
      print(msg)
      return self.answer

   def destroy(self):
      sys.modules['__builtin__'].raw_input = self.old_raw_input

"""
class Stubber(object):

   def __init__(self, func, **kwargs):
      self.old_func = func
      func = self._my_func
      self.__dict__.update(kwargs)

   def _my_func(self, *args, **kwargs):
      print('_my_func: args = %s; kwargs = %s' % args, kwargs)

   def wrap(self):

   def unwrap(self):
      sys.modules['__builtin__'].raw_input = self.old_raw_input
"""

def stubify(func):
   def _func(*args, **kwargs):
      print('_func: args = %s; kwargs = %s' % (args, kwargs))

   _func.orig = func
   return _func

def unstubify(_func):
   return _func.orig


class FileWriteCapture(object):
   """
   A class that can intercept file writes and then be queried for its
   contents.  This is very useful for capturing and verifying that
   output to sys.stdout and sys.stderr matches expectations. E.g.:

   >>> sys.stderr = FileWriteCapture(sys.stderr).StartCapture()
   >>> print >>sys.stderr, 'print',
   >>> sys.stderr.getvalue()
   'print'
   >>> sys.stderr.write(',write')
   >>> sys.stderr.getvalue()
   'print,write'
   >>> sys.stderr._buf.__class__.__name__
   'StringO'
   >>> sys.stderr.EndCapture().name
   '<stderr>'
   >>> sys.stderr._buf.__class__.__name__
   'file'
   >>> sys.stderr._buf.name
   '<stderr>'
   """

   def __init__(self, origFileObj):
      self._origFileObj = origFileObj
      self._buf = origFileObj

   def StartCapture(self):
      self._buf = StringIO()
      return self

   def EndCapture(self):
      self._buf = self._origFileObj
      return self._buf

   def __getattr__(self, attr):
      return getattr(self._buf, attr)


if __name__ == "__main__":
   import doctest
   doctest.testmod()
