#!/usr/bin/env python

"""
Tests for the getconfig and setconfig operations.
"""

import sys
sys.path.append('../operations')
sys.path.append('./stubs')
sys.path.append('..')

import unittest, testoob
from HostStub import Host
from VmStub import Vm
from Struct import Struct
from ConfigOps import GetConfig
from TableDrivenTestCase import TableDrivenTestCase
from Utils import rec_getattr


class ConfigOpsTests(TableDrivenTestCase):
   """
   Tests for the getconfig and setconfig operations.
   """
   
   testTableInputFile = file('ConfigOpsTestsTable.txt')

   @classmethod
   def createTest(cls, argsStr, key):
      def testMethod(self):
         result = GetConfig().DoIt(self.host, self.vm.name, argsStr)
         #print(result)

         self.assertEqual(result, rec_getattr(self.vm, key))

      
      testDesc = '("%s")' % argsStr
      return testDesc, testMethod

   def setUp(self):
      self.vm = Vm(name='some_vm')
      self.vm.config.guestId = 'winNetStandardGuest'
      self.vm.config.hardware = Struct(
         memoryMB = '256',
         numCPU = 2,
         )
      self.vm.config.version = 'vmx-04'
      self.vm.config.name = 'some_vm'
      self.vm.config.locationId = 'locationId'
      self.vm.config.uuid = 'uuid'
      self.vm.config.annotation = 'annotation'
      self.vm.config.files = Struct(
         snapshotDirectory = 'snapshotDir',
         suspendDirectory = 'suspendDir',
         )
      self.vm.config.flags = Struct(
         disableAcceleration = False,
         runWithDebugInfo = False,
         enableLogging = False,
         useToe = False,
         )
      self.vm.config.tools = Struct(
         afterPowerOn = False,
         afterResume = False,
         beforeGuestShutdown = False,
         beforeGuestStandby = False,
         )
      self.vm.config.defaultPowerOps = Struct(
         powerOffType = '?',
         suspendType = '?',
         resetType = '?',
         )
      
      self.host = Host('Fake host', [self.vm])

   
ConfigOpsTests.createTests()


# Start program
if __name__ == "__main__":
   testoob.main()
