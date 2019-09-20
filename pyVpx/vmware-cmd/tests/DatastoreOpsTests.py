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
from Struct import Struct
from DatastoreOps import ListDatastores, CreateNasDatastore, RemoveDatastore


class Datastore(object):

   def __init__(self, name, url, freeSpace=0, accessible=True):
      self.summary = Struct(
         name=name,
         url=url,
         freeSpace=freeSpace,
         accessible=accessible)

   @property
   def name(self): return self.summary.name

   @property
   def url(self): return self.summary.url

   @property
   def freeSpace(self): return self.summary.freeSpace


class NasVolumeSpecification(object):

   def __init__(self,
                localPath,
                remoteHost, remotePath,
                accessMode='readWrite'):
      self.localPath = localPath
      self.remoteHost = remoteHost
      self.remotePath = remotePath
      self.accessMode = accessMode


def GetHost(name, vmList, dsList,
            CreateNasDatastore=None,
            RemoveDatastore=None,
            GetDatastoreByName=None):
   host = Host(
      name,
      vmList=vmList,
      hostSystem=Struct(datastore=dsList),
      datastoreSystem=Struct())

   if CreateNasDatastore is not None:
      host.datastoreSystem.CreateNasDatastore = CreateNasDatastore
   if RemoveDatastore is not None:
      host.datastoreSystem.RemoveDatastore = RemoveDatastore
   if GetDatastoreByName is not None:
      host.GetDatastoreByName = GetDatastoreByName

   return host


class DatastoreOpsTests(unittest.TestCase):

   def testListDatastores_simple(self):
      dsList = [
         Datastore(
            name='storage1',
            url='/vmfs/volumes/457d7a7c-01488e38-480b-003048322058',
            freeSpace=4826595328),
         Datastore(
            name='storage2',
            url='/vmfs/volumes/01488e38-457d7a7c-480b-003048322058',
            freeSpace=4826595328)]
      host = GetHost('Fake host', vmList=[], dsList=dsList)

      result = ListDatastores().DoIt(host)

      self.assertEqual(result, dsList)

   def testListDatastores_noDatastores(self):
      dsList = []
      host = GetHost('Fake host', vmList=[], dsList=dsList)

      result = ListDatastores().DoIt(host)

      self.failIf(result != dsList)

   def assertEqualNasVolumeSpec(self, a1, a2):
      self.assertEqual(a1.localPath, a2.localPath)
      self.assertEqual(a1.remoteHost, a2.remoteHost)
      self.assertEqual(a1.remotePath, a2.remotePath)
      self.assertEqual(a1.accessMode, a2.accessMode)

   def testCreateNasDatastore(self):
      spec = NasVolumeSpecification(
         localPath='/path/on/local/host',
         remoteHost='remotehost.eng.vmware.com',
         remotePath='/path/on/remote/host',
         accessMode='readWrite')

      def _CreateNasDatastore(nasVolumeSpec):
         """
         Verify that we're called with a nasVolumeSpec that matches
         what we asked for.
         """

         self.assertEqualNasVolumeSpec(nasVolumeSpec, spec)
         return Datastore(name='dsName', url=spec.localPath)

      host = GetHost(
         'Fake host',
         vmList=[], dsList=[],
         CreateNasDatastore=_CreateNasDatastore)

      result = CreateNasDatastore().DoIt(
         host,
         localPath=spec.localPath,
         remoteHost=spec.remoteHost,
         remotePath=spec.remotePath,
         accessMode=spec.accessMode)

      self.assertTrue(result is not None)

   def testRemoveDatastore(self):
      datastoreNameToRemove = 'some_datastore'

      def _RemoveDatastore(datastore):
         """
         Verify that we're called with a datastore whose name matches
         the datastoreNameToRemove
         """

         self.assertEqual(datastore.name, datastoreNameToRemove)

      def _GetDatastoreByName(datastoreName):
         return Datastore(
            datastoreName,
            url='/vmfs/volumes/457d7a7c-01488e38-480b-003048322058')

      host = GetHost(
         name='Fake host',
         vmList=[],
         dsList=[],
         RemoveDatastore=_RemoveDatastore,
         GetDatastoreByName=_GetDatastoreByName)

      result = RemoveDatastore().DoIt(host, datastoreNameToRemove)

      self.assertTrue(result is not None)


# Start program
if __name__ == "__main__":
   testoob.main()
