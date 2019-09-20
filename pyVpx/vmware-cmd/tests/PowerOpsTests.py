#!/usr/bin/env python

"""
"""

import sys
sys.path.append('../operations')
sys.path.append('./stubs')
sys.path.append('..')

import unittest, testoob
from HostStub import Host
from VmStub import Vm, vim
from TaskStub import Task
from PowerOps import Start, Stop, Reset, Suspend
from TableDrivenTestCase import TableDrivenTestCase


##
## These are used for brevity in the test table data:
##
soft       = 'soft'
trysoft    = 'trysoft'
hard       = 'hard'
off        = 'off'
on         = 'on'
suspended  = 'suspended'
OK         = 'OK'
IPS        = 'IPS'
IPM        = 'IPM'
TU         = 'TU'

exceptions = {
   OK   :  None,
   IPS  :  vim.fault.InvalidPowerState,
   IPM  :  RuntimeError,  # InvalidPowerOpMode
   TU   :  vim.fault.ToolsUnavailable,
   }


class PowerOpsTests(TableDrivenTestCase):

   testTableInputFile = file('PowerOpsTestsTable.txt')

   @classmethod
   def createTest(cls,
                  operation,
                  powerOpMode,
                  startState,
                  toolsInstalled,
                  newState,
                  raisesFault,
                  callCounts):

      operation = eval(operation)
      powerOpMode = eval(powerOpMode)
      startState = eval(startState)
      toolsInstalled = eval(toolsInstalled)
      newState = eval(newState)
      raisesFault = eval(raisesFault)
      callCounts = eval(callCounts)

      def getVmAndHost():
         vm = Vm(name='fake_vm',
                 powerState=startState,
                 toolsInstalled=toolsInstalled)
         host = Host('Fake host', [vm])

         return vm, host

      def getKeywordArgs():
         kwargs = {}
         if powerOpMode is not None:
            kwargs['powerOpMode'] = powerOpMode

         return kwargs

      def testMethod(self):
         vm, host   = getVmAndHost()
         args       = (host, vm.name)
         kwargs     = getKeywordArgs()
         opFunc     = operation().DoIt
         exception  = exceptions[raisesFault]

         if exception:
            self.failUnlessRaises(exception, opFunc, *args, **kwargs)
         else:
            task = opFunc(*args, **kwargs)
            self.failIf(not isinstance(task, Task))
            task.WaitForCompletion()

         self.failIf(vm.powerState != newState)
         self.failUnlessMockCallCountsEqual(vm, callCounts)

      def getTestDesc():
         if toolsInstalled: toolsInstalledStr = 'tools'
         else:              toolsInstalledStr = 'noTools'

         result = getattr(raisesFault, '__name__', None) or raisesFault

         opName = operation.__name__

         return ('(%s, %s, %s, %s) => (%s, %s)'
                 % (opName, powerOpMode, startState, toolsInstalledStr,
                    result, newState))

      return getTestDesc(), testMethod


PowerOpsTests.createTests()


# Start program
if __name__ == "__main__":
   testoob.main()
