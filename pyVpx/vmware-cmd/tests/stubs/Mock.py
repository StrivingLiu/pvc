#!/usr/bin/env python

"""
"""

import sys
sys.path.append('../operations')
sys.path.append('./stubs')
sys.path.append('..')

import unittest, testoob


class Mock(object):
   """
   A simple Mock object class.

   It logs and counts method calls so that tests can check that the
   SUT is invoking the mock in the expected way. E.g.:

    >>> door = Door()
    >>> door.Open()
    >>> door.Close()
    >>> door.Open()
    >>> door.Open.callCount
    2
    >>> door.Close.callCount
    1
   """

   def __init__(self, *args, **kwargs):
      """
      >>> door = Door()
      >>> door.Open.callCount
      0
      >>> door.Close.callCount
      0
      """

      self.calls = []

      for attrName in dir(self):
         if attrName.startswith('_'): continue
         attr = getattr(self, attrName, None)
         if callable(attr):
            wrappedMethod = self.wrapMethod(attr)
            wrappedMethod.callCount = 0
            setattr(self, attrName, wrappedMethod)

   def wrapMethod(self, origMethod):
      """
      >>> class Dog:
      ...   def Bark(self): return '*bark*'
      >>>
      >>> dog = Dog()
      >>> wrappedMethod = Mock().wrapMethod(dog.Bark)
      >>> wrappedMethod.callCount = 0
      >>>
      >>> wrappedMethod()
      '*bark*'
      >>> wrappedMethod.callCount
      1
      >>> wrappedMethod()
      '*bark*'
      >>> wrappedMethod.callCount
      2
      """

      def _incrementCallCount():
         setattr(_newMethod, 'callCount',
                 1 + getattr(_newMethod, 'callCount'))

      def _newMethod(*args, **kwargs):
         _incrementCallCount()
         self.calls.append(dict(methodName=origMethod.__name__))
         return origMethod(*args, **kwargs)

      return _newMethod


class MockTests(unittest.TestCase):
   """
   Test the Mock class.

   >>> MockTests
   <class '__main__.MockTests'>
   """

   def test_it(self):
      """
      >>> MockTests.test_it
      <unbound method MockTests.test_it>
      """

      door = Door()
      door.Open()
      door.Close()
      door.Open()

      self.failIf(door.calls != [{'methodName': 'Open'},
                                 {'methodName': 'Close'},
                                 {'methodName': 'Open'}])
      self.failIf(door.Open.callCount != 2)
      self.failIf(door.Close.callCount != 1)


class Door(Mock):
   """
   Simple class used for testing

   >>> door = Door()
   """

   def Open(self):
      """
      >>> door = Door()
      >>> door.Open()
      """

   def Close(self):
      """
      >>> door = Door()
      >>> door.Close()
      """


# Start program
if __name__ == "__main__":
   import doctest
   doctest.testmod()
   print
   testoob.main()
