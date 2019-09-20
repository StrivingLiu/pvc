#!/usr/bin/env python

"""
Test the CommandProcessor class, verifying:

 * Registration and retrieval of operations
 * Argument processing
 * Operation execution, including operations that return a Task
"""

import sys
sys.path.append('../operations')
sys.path.append('./stubs')
sys.path.append('..')

import unittest, testoob
from HostStub import Host
from VmStub import Vm, vim
from TaskStub import Task
import CommandProcessor
from Operation import Operation
from TestUtils import FileWriteCapture


class CommandProcessorTests(unittest.TestCase):

   redirect_stdout = True
   redirect_stderr = True

   def setUp(self):
      self.host = Host('fakehost',
                       vmList=[Vm(name='FakeVm',
                                  powerState='poweredOn')])

      ## Capture what the SUT is writing to stdout and stderr so that
      ## we can verify it later.
      if self.redirect_stdout:
         sys.stdout = FileWriteCapture(sys.stdout).StartCapture()
      if self.redirect_stderr:
         sys.stderr = FileWriteCapture(sys.stderr).StartCapture()

   def tearDown(self):
      ## Revert to the normal sys.stdout and sys.stderr
      if self.redirect_stderr:
         sys.stderr = sys.stderr.EndCapture()
      if self.redirect_stdout:
         sys.stdout = sys.stdout.EndCapture()

   def test_004_Process_noOptionsAndNoArgs(self):
      """
      Call Process with no options and no args and verify that an
      exception is raised.
      """

      self.assertRaises(
         CommandProcessor.InvalidOperation,
         CommandProcessor.Process, self.host, [])

   def test_004_Process_vmoperation(self):
      """
      Test invoking an operation that returns vm powerState.
      """

      result = CommandProcessor.Process(
         host=self.host,
         args=['vmoperation', 'FakeVm'])

      self.assertEqual(result[0], 'vmoperation')
      self.assertEqual(result[1], self.host.GetVm('FakeVm').powerState)

   def test_004_Process_returnarg(self):
      """
      Test invoking an operation that returns the arg passed to it.
      """

      result = CommandProcessor.Process(
         host=self.host,
         args=['returnarg', 'foo'])

      self.assertEqual(result, ('returnarg', 'foo'))

   def test_004_Process_raiseexception(self):
      """
      Invoke an operation that raises an exception and verify that an
      error message with the exception message gets written to
      sys.stderr
      """

      ## Raise the exception that we expect CommandProcessor.Process
      ## to raise in a bit, so that we know what the exception message
      ## looks like and don't have to duplicate it here in the test
      ## and make the test fragile.
      try:
         RaiseException().DoIt(None)
      except vim.fault.InvalidState, e:
         exceptionMsg = e.msg

      CommandProcessor.Process(host=self.host, args=['raiseexception'])

      if hasattr(sys.stderr, 'getvalue'):
         self.assertEqual(sys.stderr.getvalue(),
                          'vim.fault.InvalidState: %s\n' % exceptionMsg)

   def test_004_Process_returnsatask(self):
      """
      Test invoking an operation that returns a Task.
      """

      returnValue = 'returnValue'

      result = CommandProcessor.Process(
         host=self.host,
         args=['returnsatask', returnValue])

      self.assertEqual(result[0], 'returnsatask')
      self.assertTrue(isinstance(result[1], Task))

   def test_ProcessArgs(self):
      """
      Test that given a list of args with one that represents a
      registered operation, CommandProcesor.ProcessArgs returns a list
      of args that are not the registered operation.
      """

      result = CommandProcessor._ProcessArgs(self.host,
                                             ['returnarg', 'foo', 'bar'])

      self.assertEqual(result, ['foo', 'bar'])

   def test_ProcessArgs_unknownOperation(self):
      """
      Test that given a list of args with none that represent a
      registered operation, CommandProcesor.ProcessArgs returns a list
      of args that are not the registered operation - i.e.: all the
      args.
      """

      result = CommandProcessor._ProcessArgs(self.host,
                                             ['unknownop', 'foo', 'bar'])

      self.assertEqual(result, ['unknownop', 'foo', 'bar'])

   def test_ProcessArgs_emptyArgs(self):
      """
      Test that given an empty list of args,
      CommandProcesor.ProcessArgs returns an empty list.
      """

      result = CommandProcessor._ProcessArgs(self.host, [])

      self.assertEqual(result, [])


class VmOperation(Operation):
   """
   An operation that returns a vm's powerState
   """

   def DoIt(self, host, vm):
      return Operation.GetVm(host, vm).powerState

class ReturnArg(Operation):
   """
   An operation that simply returns the arg passed to it
   """

   def DoIt(self, host, arg):
      return arg

class RaiseException(Operation):
   """
   An operation that simply raises an exception
   """

   def DoIt(self, host):
      raise vim.fault.InvalidState(
         msg='This is a bogus exception, just for testing.')

class ReturnsATask(Operation):
   """
   An operation that returns a Task that sleeps for a little while
   before returning passed in value
   """

   def DoIt(self, host, returnValue):
      return Task(taskName='ReturnsATask',
                  sleepSeconds=1,
                  func=id,
                  returnValue=returnValue)



class OperationsStub(object):

   def __init__(self):
      self.opsDict = {
         'vmoperation'      : VmOperation,
         'returnarg'        : ReturnArg,
         'raiseexception'   : RaiseException,
         'returnsatask'     : ReturnsATask }

   def GetOperationByName(self, name):
      ## `name` must be a string
      if not hasattr(name, 'endswith'): return None
      
      opClass = self.opsDict.get(name, None)

      if opClass:  return opClass()
      else:        return None


CommandProcessor.operations = OperationsStub()


# Start program
if __name__ == "__main__":
   testoob.main()
