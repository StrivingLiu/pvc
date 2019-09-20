#!/usr/bin/env python

"""
"""

import sys
sys.path.append('../operations')
sys.path.append('./stubs')
sys.path.append('..')

import unittest, testoob
from Host import NullHost, NotConnected
from HostStub import Host
from VmStub import Vm
from ListVms import ListVms


class ListVmsTests(unittest.TestCase):

   def testNormal(self):
      host = Host('Fake host', [
         Vm('Marc'),
         Vm('Nicole'),
         Vm('Linux'),
         ])

      result = ListVms().DoIt(host)

      expectedResult = [
         Vm("Marc", host=host),
         Vm("Nicole", host=host),
         Vm("Linux", host=host),
         ]

      self.failIf(result != expectedResult, 'ListVms returns correct vms')

   def testNoVms(self):
      host = Host('Fake host', [])

      result = ListVms().DoIt(host)

      self.failIf(result != [], 'ListVms returns correct vms')

   def testNullHost(self):
      host = NullHost('nullhost')

      self.failUnlessRaises(NotConnected, ListVms().DoIt, host)


# Start program
if __name__ == "__main__":
   testoob.main()
