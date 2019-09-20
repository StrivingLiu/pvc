"""
@file Struct.py

This file defines a simple class called Struct that is surprisingly useful.
"""

class Struct(object):
   """
   Super simple class for quickly crating data-only objects with
   attributes, kind of like structs in C, C++, and Java.

   This simple class is surprisingly useful.

   Example usage:

   employeeData = Struct(employeeName='Jacob', directReports=[
      Struct(employeeName='Richard'),
      Struct(employeeName='Ben', directReports=[
         Struct(employeeName='Julia'),
         Struct(employeeName='Tom', directReports=[
            Struct(employeeName='Michael'),
         ]),
         Struct(employeeName='Goodwin'),
      ]),
      Struct(employeeName='John', directReports=[
         Struct(employeeName='Sawyer'),
         Struct(employeeName='Claire'),
      ]),
   ])
   """

   def __init__(self, **kw):
      """
      Simply copy any keyword arguments to the object's internal
      dictionary.
      """

      self.__dict__ = kw
