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


class VmTests(unittest.TestCase):

   def setUp(self):
      pass

   def failIfNotTask(self, task, msg):
      self.failIf(not hasattr(task, 'WaitForCompletion'), msg)

   def test_PowerOn_off_ok(self):
      vm = Vm(name='OffToOn', powerState='off')

      task = vm.PowerOn()

      self.failIfNotTask(task, 'PowerOn return value was not a Task')
      self.failIf(task.WaitForCompletion() != 'success')
      self.failIf(vm.powerState != 'on')

   def test_PowerOn_on_fails(self):
      vm = Vm(name='OnToOn', powerState='on')

      self.failUnlessRaises(vim.fault.InvalidPowerState, vm.PowerOn)

   def test_PowerOff_on_ok(self):
      vm = Vm(name='OnToOff', powerState='on')

      task = vm.PowerOff()

      self.failIfNotTask(task, 'PowerOff return value was not a Task')
      self.failIf(task.WaitForCompletion() != 'success')
      self.failIf(vm.powerState != 'off')

   def test_PowerOff_off_fails(self):
      vm = Vm(name='OffToOff', powerState='off')

      self.failUnlessRaises(vim.fault.InvalidPowerState, vm.PowerOff)

   def test_ShutdownGuest_on_ok(self):
      vm = Vm(name='OnToOff', powerState='on')

      task = vm.ShutdownGuest()

      self.failIfNotTask(task, 'ShutdownGuest return value was not a Task')
      self.failIf(task.WaitForCompletion() != 'success')
      self.failIf(vm.powerState != 'off')

   def test_ShutdownGuest_off_fails(self):
      vm = Vm(name='OffToOff', powerState='off')

      self.failUnlessRaises(vim.fault.InvalidPowerState, vm.ShutdownGuest)

   def test_Reset_on_ok(self):
      vm = Vm(name='OnReset', powerState='on')

      task = vm.Reset()

      self.failIfNotTask(task, 'Reset return value was not a Task')
      self.failIf(task.WaitForCompletion() != 'success')
      self.failIf(vm.powerState != 'on')

   def test_Reset_off_fails(self):
      vm = Vm(name='OffReset', powerState='off')

      self.failUnlessRaises(vim.fault.InvalidPowerState, vm.Reset)

   def test_RebootGuest_on_ok(self):
      vm = Vm(name='OnRebootGuest', powerState='on')

      task = vm.RebootGuest()

      self.failIfNotTask(task, 'RebootGuest return value was not a Task')
      self.failIf(task.WaitForCompletion() != 'success')
      self.failIf(vm.powerState != 'on')

   def test_RebootGuest_off_fails(self):
      vm = Vm(name='OffRebootGuest', powerState='off')

      self.failUnlessRaises(vim.fault.InvalidPowerState, vm.RebootGuest)

   def test_Suspend_on_ok(self):
      vm = Vm(name='OnSuspend', powerState='on')

      task = vm.Suspend()

      self.failIfNotTask(task, 'Suspend return value was not a Task')
      self.failIf(task.WaitForCompletion() != 'success')
      self.failIf(vm.powerState != 'suspended')

   def test_Suspend_off_fails(self):
      vm = Vm(name='OffSuspend', powerState='off')

      self.failUnlessRaises(vim.fault.InvalidPowerState, vm.Suspend)

   def test_StandbyGuest_on_ok(self):
      vm = Vm(name='OnToOff', powerState='on')

      task = vm.StandbyGuest()

      self.failIfNotTask(task, 'StandbyGuest return value was not a Task')
      self.failIf(task.WaitForCompletion() != 'success')
      self.failIf(vm.powerState != 'suspended')

   def test_StandbyGuest_off_fails(self):
      vm = Vm(name='OffToOff', powerState='off')

      self.failUnlessRaises(vim.fault.InvalidPowerState, vm.StandbyGuest)


# Start program
if __name__ == "__main__":
   testoob.main()
