#!/usr/bin/env python

"""
"""

import sys
sys.path.append('../operations')
sys.path.append('./stubs')
sys.path.append('..')

import unittest, testoob
from HostStub import Host, pyVmomi
from VmStub import Vm


class HostTests(unittest.TestCase):

   def setUp(self):
      self.hostName = 'Fake host'
      self.vmName = 'Marc'
      self.host = Host(self.hostName,
                       [Vm(self.vmName, powerState='poweredOff')])

   def test_hostname(self):
      self.failIf(self.host.hostname != self.hostName)

   def test_Connect(self):
      self.host.Connect()

   def test_GetVm_valid(self):
      vm = self.host.GetVm(self.vmName)

      self.failIf(not isinstance(vm, Vm))
      self.failIf(vm.host != self.host)

   def test_GetVm_nonexistent(self):
      self.failUnlessRaises(pyVmomi.vim.fault.NotFound,
                            self.host.GetVm, 'unknownVm')

   def test_GetVm_None(self):
      self.failUnlessRaises(pyVmomi.vim.fault.NotFound,
                            self.host.GetVm, None)

   def test_GetVms(self):
      vms = self.host.GetVms()

      self.failIf(not isinstance(vms, list))
      self.failIf(vms[0] != self.host.GetVm(self.vmName))


# Start program
if __name__ == "__main__":
   testoob.main()
