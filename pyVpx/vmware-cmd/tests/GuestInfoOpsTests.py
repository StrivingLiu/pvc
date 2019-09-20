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
from Nic import Nic
from GuestInfoOps import ListGuestNics
from Struct import Struct


class GuestInfoOpsTests(unittest.TestCase):

   def setUp(self):
      self.guest_net = [
         Struct(connected=True,
                deviceConfigId=4001,
                ipAddress='169.254.145.89',
                macAddress='00:0c:29:d9:60:4c',
                network='vctportgroup'),
         Struct(connected=True,
                deviceConfigId=4000,
                ipAddress='10.20.153.42',
                macAddress='00:0c:29:d9:60:42',
                network='VMPublic'),
      ]
      self.expected2Nics = map(Nic, self.guest_net)
      self.expected1Nic = map(Nic, self.guest_net[1:])
      self.vmWith2Nics = Vm(name='vmWith2Nics')
      self.vmWith2Nics.guest.net = self.guest_net
      self.vmWith1Nic = Vm(name='vmWith1Nic')
      self.vmWith1Nic.guest.net = self.guest_net[1:]
      self.vmWith0Nics = Vm(name='vmWith0Nics')
      self.vmWith0Nics.guest.net = []
      self.vmWithNoGuestInfo = Vm(name='vmWithNoGuestInfo')
      self.vmWithNoGuestInfo.guest.net = None
      self.host = Host('Fake host', [self.vmWith2Nics,
                                     self.vmWith1Nic,
                                     self.vmWith0Nics,
                                     self.vmWithNoGuestInfo])

   def test_listguestnics_vmWith2Nics(self):
      result = ListGuestNics().DoIt(self.host, self.vmWith2Nics.name)

      #print(result)
      self.assertEqual(result, self.expected2Nics)

   def test_listguestnics_vmWith1Nic(self):
      result = ListGuestNics().DoIt(self.host, self.vmWith1Nic.name)

      #print(result)
      self.assertEqual(result, self.expected1Nic)

   def test_listguestnics_vmWith0Nics(self):
      result = ListGuestNics().DoIt(self.host, self.vmWith0Nics.name)

      #print(result)
      self.assertEqual(result, [])

   def test_listguestnics_vmWithNoGuestInfo(self):
      result = ListGuestNics().DoIt(self.host, self.vmWithNoGuestInfo.name)

      #print(result)
      self.assertEqual(result, None)

   def test_listguestnics_unknownVm(self):
      self.assertRaises(pyVmomi.vim.fault.NotFound,
                        ListGuestNics().DoIt, self.host, 'unknownVm')


# Start program
if __name__ == "__main__":
   testoob.main()
