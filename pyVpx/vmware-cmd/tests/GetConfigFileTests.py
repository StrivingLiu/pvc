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
from GetConfigFile import GetConfigFile


class GetConfigFileTests(unittest.TestCase):

   def setUp(self):
      self.vm = Vm(name='some_vm')
      self.vm.localPath = '/fake/vmfs/volumes/fake_datastore/%s.vmx' \
                          % self.vm.name
      self.host = Host('Fake host', [self.vm])

   def test_GetConfigFile_ok(self):
      result = GetConfigFile().DoIt(self.host, self.vm.name)

      self.failIf(result != self.vm.localPath)

   def test_GetConfigFile_unknownVm(self):
      """
      Verify that we raise an appropriate exception if the operation
      is invoked with an unknown vm name.
      """

      self.failUnlessRaises(pyVmomi.vim.fault.NotFound,
                            GetConfigFile().DoIt, self.host, 'unknownVm')


# Start program
if __name__ == "__main__":
   testoob.main()
