#!/usr/bin/python

# Exercises the virtual disk manager code.
#
# Creates and messes with a bunch of virtual disks.
# Request one datastore to be present, with about 200MB of free space
# Does not touch existing files/directories in the datastore.
#
# @todo:
# - Add more negative test cases.
# - Create and play with some directories too

# November 24, 2014
# It was noted in passing that this unit test exposed Bug 968456.
# This exposure was coincidental with the fact that this unit test was failing
# because of unsatisfied expectations of the host, such as datastore size.
# Most of these original 'failures' were not addressed as they were out of scope
# for the bug fix, only the fixed size request for 1 TeraByte of space by
# OptimizeEqgerZero was reduced to allow complete and successful execution;
# this and other issues should  be addressed with the upcoming unit test
# framework effort.
#
# Added one test, 'TestInsufficientCapacity' for Bug968456.  Arguably this test
# should be for a different unit, 'PlatformError2Faults', and shoud be moved
# during the unit test framework migration.

from __future__ import print_function

import os
import sys
from pyVmomi import Vim
from pyVmomi import Vmodl
from pyVim.connect import SmartConnect
from pyVim.task import WaitForTask
from pyVim import host
from pyVim import invt
from pyVim import arguments
from pyVim.helpers import Log,StopWatch
import time
import re

#gCreateTypes=["thick", "thin", "preallocated", "eagerZeroedThick"]
gCreateTypes=["preallocated"]
gNonCreateTypes=["sparse2Gb", "thick2Gb", "flatMonolithic", "sparseMonolithic"]
gAdapterTypes=["busLogic", "lsiLogic", "ide"]

class Phase:
   def __init__(self):
      self.phaseNumber = 0
      self.phaseClock = StopWatch()

   def SetPhase(self, msg):
      Log("Phase " + str(self.phaseNumber) + ": " + msg + " completed")
      self.phaseClock.finish("phase " + str(self.phaseNumber))
      self.phaseClock = StopWatch()
      self.phaseNumber = self.phaseNumber + 1

#
# Helper routine to create a NAS Datastore on the host
#
def CreateNasDs(dsName, remoteHost, remotePath):
    try:
        Log("Creating NAS datastore " + dsName + " ...")
        spec = Vim.Host.NasVolume.Specification()
        spec.SetAccessMode("readWrite")
        spec.SetLocalPath(dsName)
        spec.SetRemoteHost(remoteHost)
        spec.SetRemotePath(remotePath)
        print(spec)

        nasDs = datastoreSystem.CreateNasDatastore(spec)
        if nasDs == None or nasDs.GetSummary().GetName() != dsName:
            Log("Failed to create datastore")
            return None
        else:
            Log("Successfully created datastore " + dsName)
            return nasDs
    except Exception as e:
        Log("Failed to create datastore " + str(e))
        return None


#
# Helper routine to destroy a NAS datastores
#
def DestroyNasDs(dsName):
    for datastore in datastoreSystem.GetDatastore():
        if datastore.GetSummary().GetName() == dsName:
            datastore.Destroy()
            break


# Tests for VirtualDiskManager managed object
class VirtualDiskManagerTest:

   def __init__(self, virtualDiskManager, args):
      self._vdm = virtualDiskManager
      self._dc = invt.GetDatacenter()
      self._dsName = args.GetKeyValue("ds")
      self._rdm = args.GetKeyValue("rdm")
      self._nas = args.GetKeyValue("nas")
#     self._subdir = args.GetKeyValue("subdir")
      self._subdir = "";

   def FindDatastore(self):
      envBrowser = invt.GetEnv()
      cfgTarget = envBrowser.QueryConfigTarget(None)
      dsList = cfgTarget.GetDatastore()
      if not dsList:
          raise Exception("No datastore available to create VM.")
      dsName = None
      for ds in dsList:
          if ds.GetDatastore().GetAccessible():
              dsRef = ds.GetDatastore()
              break
      if dsRef == None:
          raise Exception("No available datastore")
      return dsRef

   def FindDatastoreName(self):
      envBrowser = invt.GetEnv()
      cfgTarget = envBrowser.QueryConfigTarget(None)
      dsList = cfgTarget.GetDatastore()
      if not dsList:
          raise Exception("No datastore available to create VM.")
      dsName = None
      for ds in dsList:
          if ds.GetDatastore().GetAccessible():
              dsName = ds.GetDatastore().GetName()
              break
      if dsName == None:
          raise Exception("No available datastore")
      return dsName

   def RunTests(self):
      Log("VirtualDiskManager: Run tests")
      if self._dsName == None:
         self._dsName = self.FindDatastoreName()

      self.TestCreateFileBacked()
      self.TestCreateFileBackedWeirdPaths()
      self.TestMove()
      self.TestUuid()
      #self.TestExtend()
      self.TestCopy()
      self.TestCopySelf()
      self.TestCopySpecless()
      self.TestEagerZero()
      self.TestOptimizeEagerZero()
      self.TestInflate()
      if self._rdm != None:
         self.TestCreateDeviceBacked()
      ##self.TestDelete()
      self.TestQueryDiskInfo()
      self.TestInsufficientCapacity()

   def MakeDsPath(self, name, subdir=""):
      path = "[" + self._dsName + "] " + subdir + name + ".vmdk"
      return path

   def CreateSingle(self, name="vdmt_single_preallocated", type="preallocated",
                    size=50000, subdir=""):
      spec = Vim.VirtualDiskManager.FileBackedVirtualDiskSpec()
      spec.SetDiskType(type)
      spec.SetAdapterType("busLogic")
#      spec.SetCapacityKb(long(50000))
      spec.SetCapacityKb(size)
      path = self.MakeDsPath(name, subdir)
      Log("Creating disk (" + path + ").")
      task = self._vdm.CreateVirtualDisk(path, None, spec)
      WaitForTask(task)
      Log("Creating disk (" + path + ") Done.")
      return path

   def CreateRdm(self, devicePath, name="vdmt_rdm", type="rdmp"):
      path = self.MakeDsPath(name)
      spec = Vim.VirtualDiskManager.DeviceBackedVirtualDiskSpec()
      spec.SetDevice(devicePath)
      spec.SetDiskType(type)
      spec.SetAdapterType("busLogic")
      path = self.MakeDsPath(name)
      Log("Creating rdm disk (" + path + ").")
      task = self._vdm.CreateVirtualDisk(path, None, spec)
      WaitForTask(task)
      Log("Creating rdm disk (" + path + ") Done.")
      return path

   def CreateChild(self, parent, name="vdmt_child", subdir=""):
      path = self.MakeDsPath(name, subdir)
      Log("Creating child disk (" + path + ").")
      return self.CreateChildWithPath(parent, path)

   def CreateChildWithPath(self, parent, path):
      Log("Creating child disk (" + path + ").")
      task = self._vdm.CreateChildDisk(path, None, parent, None)
      WaitForTask(task)
      Log("Creating child disk (" + path + ") Done.")
      return path

   def DeleteSingle(self, path):
      Log("Deleting disk (" + path + ").")
      task = self._vdm.DeleteVirtualDisk(path, None)
      WaitForTask(task)
      Log("Deleting disk (" + path + ") Done.")

   def TestCreateFileBacked(self, cleanup=True, sizeMB=50,
                            adapterType="busLogic"):
      Log("VirtualDiskManager: Create file-backed tests")
      spec = Vim.VirtualDiskManager.FileBackedVirtualDiskSpec()

      for t in gCreateTypes:
         Log("  Creating disk of type " + t + "...")
         spec.SetDiskType(t)
         spec.SetAdapterType(adapterType)
         spec.SetCapacityKb(long(sizeMB*1000))

         path = self.MakeDsPath("vdmt_" + `sizeMB` + "mb_" + t)
         task = self._vdm.CreateVirtualDisk(path, None, spec)
         WaitForTask(task)
         Log("  Creating disk of type " + t + " Done.")

         if cleanup:
            task = self._vdm.DeleteVirtualDisk(path, None)
            Log("  Deleting disk of type " + t + " Done.")

   def TestCreateFileBackedWeirdPaths(self, cleanup=True):
      Log("VirtualDiskManager: Create file-backed tests with weird paths")
      spec = Vim.VirtualDiskManager.FileBackedVirtualDiskSpec()

      weirdNames = [
           # directory-looking path without vmdk extension handled like disks
           [True, "path without vmdk extension" , "novmdkext"],
           # created but disklib errored on reading disk info IIRC
           [False, "path with quotes and stuff", "\"\",.-.vmdk"],
           [False, "path with special characters",
                   "~!@#$%^&*-_=+[]\\{}|;:\",./<>?-.vmdk"],
           [False, "path with single quote not liked by vmfs",
                   "\"xxxquote.vmdk"],
           [False, "nonexistent directory path with trailing slash disallowed",
                   "withslash/"]
      ]

      for allow,desc,name in weirdNames:
         # @todo exercise disallowed ones too, but catch/match exceptions
         if allow:
            spec.SetDiskType("preallocated")
            spec.SetAdapterType("busLogic")
            spec.SetCapacityKb(long(50000))

            path = "[" + self._dsName + "] " + name
            Log("  Creating " + desc + " (" + path + ")")
            task = self._vdm.CreateVirtualDisk(path, None, spec)
            WaitForTask(task)
            Log("  Creating " + desc + " (" + path + ") Done.")

            if cleanup:
               task = self._vdm.DeleteVirtualDisk(path, None)
               Log("  Deleting " + desc + " (" + path + ") Done.")

   def TestCreateDeviceBacked(self):
      path = self.CreateRdm(self._rdm, name="CreateDevicedBackTest")
      self.DeleteSingle(path)

   # @todo test delete nonexistent and directory paths
   def TestDelete(self):
      path = "[" + self._dsName + "] " + "iDontExist"
      task = self._vdm.DeleteVirtualDisk(path, self._dc)
      WaitForTask(task, True)

   def TestUuid(self):
      Log("VirtualDiskManager: UUID tests")
      path = self.CreateSingle("UuidTest")
      #path = 'http://host/folder/test/50mb_thin.vmdk&dsName=Storage1'

      Log("Query UUID")
      uuid = self._vdm.QueryVirtualDiskUuid(path, self._dc)
      print("uuid is " + uuid)

      Log("Set UUID")
      self._vdm.SetVirtualDiskUuid(path, self._dc,
                   "60 00 C2 92 92 fc b1 b0-11 11 11 11 11 11 11 11")

      Log("Query UUID")
      uuid = self._vdm.QueryVirtualDiskUuid(path, self._dc)
      print("uuid is " + uuid)

      self.DeleteSingle(path)

   def TestExtend(self):
      Log("VirtualDiskManager: Extend tests")
      path = self.CreateSingle("Extend")

      task = self._vdm.ExtendVirtualDisk(path, self._dc, 2097252)
      WaitForTask(task, True)

   def ValidateQueryDiskInfo(self, path, expectedDiskTypes, expectedParentPaths,
                             includeParents=True):
      Log("VirtualDiskManager: query disk info tests")
      Log("Query disk info for " + path)
      task = self._vdm.QueryVirtualDiskInfo(path, self._dc, includeParents)
      WaitForTask(task, True)
      diskInfos = task.info.result
      for i in xrange(len(expectedDiskTypes)):
         if diskInfos[i].diskType != expectedDiskTypes[i]:
            raise Exception("Unexpected disk type for %s. "
                            "Expected '%s', got '%s'" % \
                            (diskInfos[i].unit.name, expectedDiskTypes[i],
                             diskInfos[i].diskType))
      for i in xrange(len(expectedParentPaths)):
         parent = diskInfos[i].parent if diskInfos[i].parent else ""
         pathPos = expectedParentPaths[i].find('] ')+ 2 #matching relative paths
         Log("Query disk info : parent path for chain " + `i` + " = " + parent)
         if parent != expectedParentPaths[i] and \
            parent != expectedParentPaths[i][pathPos:] :
            raise Exception("Unexpected parent path for %s. "
                            "Expected '%s', got '%s'" % \
                            (diskInfos[i].unit.name, expectedParentPaths[i],
                             parent))

   def ShowDiskInfo(self, path, includeParents=True):
      Log("VirtualDiskManager: show query disk info")
      Log("Query disk info for " + path)
      task = self._vdm.QueryVirtualDiskInfo(path, self._dc, includeParents)
      WaitForTask(task, True)
      diskInfos = task.info.result
      Log("Result = \n" + `diskInfos`)

   def TestQueryDiskInfo(self):
      disksCreated = []

      nasCreated = False
      host = share = nasDsName = None
      if self._nas:
         (host, share, nasDsName) = self._nas.split(":")
         CreateNasDs(nasDsName, host, share)
         nasCreated = True

      try:
         # query child of eagerzeroed disk
         path = self.CreateSingle(name="ezt", type="eagerZeroedThick")
         disksCreated.insert(0, path)
         self.ValidateQueryDiskInfo(path, ["eagerZeroedThick"], [""])

         # query multi-link disk
         path = self.CreateSingle(name="zt", type="preallocated")
         disksCreated.insert(0, path)
         child = self.CreateChild(path, name="zt_child")
         disksCreated.insert(0, child)
         self.ValidateQueryDiskInfo(child, ["preallocated", "delta"],["", path])
         grandchild = self.CreateChild(child, name="zt_grandchild")
         disksCreated.insert(0, grandchild)
         self.ValidateQueryDiskInfo(grandchild,
               ["preallocated", "delta", "delta"],
               ["", path, child])

         # query child of inflated disk
         path = self.CreateSingle(name="thin", type="thin")
         disksCreated.insert(0, path)
         self.ValidateQueryDiskInfo(path, ["thin"], [""])
         task = self._vdm.InflateVirtualDisk(path, self._dc)
         WaitForTask(task, True)
         child = self.CreateChild(path, name="inflatedthin_child",
                                        subdir=self._subdir)
         disksCreated.insert(0, child)
         self.ValidateQueryDiskInfo(child, ["eagerZeroedThick", "delta"],
                                           ["", path])

         # query child of disk chain with links in different directories
         # possible even different datastores,
         path = self.CreateSingle(name="thin2base", type="thin")
         disksCreated.insert(0, path)
         Log("  Query disk info for " + path)
         self.ValidateQueryDiskInfo(path, ["thin"], [""])

         child = self.CreateChild(path, name="subdir_child",subdir=self._subdir)
         disksCreated.insert(0, child)
         Log("  Query disk info for " + child)
         self.ValidateQueryDiskInfo(child, ["thin", "delta"], ["", path])

         if self._nas:
            otherdsPath = '[' + nasDsName + '] otherds_grandchild.vmdk'
            grandchild = self.CreateChildWithPath(child, otherdsPath)
         else:
            grandchild = self.CreateChild(child, name="subdir_grandchild",
                                                 subdir=self._subdir)

         disksCreated.insert(0, grandchild)
         Log("  Query disk info for " + grandchild)
         self.ValidateQueryDiskInfo(grandchild, ["thin", "delta", "delta"],
                                                ["", path, child])

         ggrandchild = self.CreateChild(grandchild, name="gg_child",
                                                    subdir=self._subdir)
         disksCreated.insert(0, ggrandchild)
         Log("  Query disk info for " + ggrandchild)

         if self._nas:
            Log("Bringing down datastore of parent disk")
            DestroyNasDs(nasDsName)
            nasCreated = False

         # Query disk info a disk link with inaccessible parent should succeed.
         Log("  Show disk info for " + ggrandchild)
         self.ShowDiskInfo(ggrandchild, includeParents=False)

         # query rdm disk
         if self._rdm != None:
            path = self.CreateRdm(self._rdm, name="rdmp")
            disksCreated.insert(0, path)
            self.ValidateQueryDiskInfo(path, ["rdmp"], [""])
      finally:
         if self._nas and not nasCreated:
            # Remount NAS datastore for cleanup
            CreateNasDs(nasDsName, host, share)
            nasCreated = True
         for path in disksCreated:
            self.DeleteSingle(path)

      if self._nas and nasCreated:
         DestroyNasDs(nasDsName)

   def TestCopySpecless(self):
      Log("VirtualDiskManager: Copy test without spec")
      pathA = self.CreateSingle("CopyTestSpecLess")
      pathB = self.MakeDsPath("CopyTestSpecLess_copy")
      Log("  Copying: " + pathA + " -> " + pathB)
      task = self._vdm.CopyVirtualDisk(pathA, self._dc,
                                       pathB, self._dc, None, True)
      WaitForTask(task, True)
      self.DeleteSingle(pathA)
      self.DeleteSingle(pathB)

   def TestCopy(self, targetDiskType="thin", targetAdapterType="lsiLogic"):
      Log("VirtualDiskManager: Copy test")
      spec = Vim.VirtualDiskManager.FileBackedVirtualDiskSpec()
      spec.capacityKb = long(10000)
      spec.diskType = targetDiskType
      spec.adapterType = targetAdapterType

      pathA = self.CreateSingle("CopyTest")
      pathB = self.MakeDsPath("CopyTest_copy_" + targetDiskType)
      Log("  Copying: " + pathA + " -> " + pathB)
      task = self._vdm.CopyVirtualDisk(pathA, self._dc,
                                       pathB, self._dc, spec, True)
      WaitForTask(task, True)
      self.DeleteSingle(pathA)
      self.DeleteSingle(pathB)

   def TestCopySelf(self, targetDiskType="thin", targetAdapterType="lsiLogic"):
      Log("VirtualDiskManager: Copy self test")
      spec = Vim.VirtualDiskManager.FileBackedVirtualDiskSpec()
      spec.capacityKb = long(10000)
      spec.diskType = targetDiskType
      spec.adapterType = targetAdapterType

      path = self.CreateSingle("CopySelfTest")
      Log("  Copying Self (no-op): " + path)
      task = self._vdm.CopyVirtualDisk(path, self._dc,
                                       path, self._dc, spec, True)
      WaitForTask(task, True)
      self.DeleteSingle(path)

   def TestMove(self):
      pathA = self.CreateSingle("MoveTest")
      pathB = self.MakeDsPath("MoveTest_move")
      Log("  Moving: " + pathA + " -> " + pathB)
      task = self._vdm.MoveVirtualDisk(pathA, self._dc,
                                       pathB, self._dc, True)
      WaitForTask(task, True)

      Log("  Moving back: " + pathB + " -> " + pathA)
      task = self._vdm.MoveVirtualDisk(pathB, self._dc,
                                       pathA, self._dc, True)
      WaitForTask(task, True)

      self.DeleteSingle(pathA)


   def TestEagerZero(self):
      Log("VirtualDiskManager: Eagerzero test")
      path = self.CreateSingle("EagerZeroTest", "preallocated")
      Log("  EagerZeroing: " + path)
      task = self._vdm.EagerZeroVirtualDisk(path)
      WaitForTask(task, True)
      self.DeleteSingle(path)


   def TestOptimizeEagerZero(self):
      ph = Phase()
      path = self.CreateSingle("OptimizeEagerZeroTest1", "preallocated",
#                                1000000000, subdir=self._subdir)
                                1000000, subdir=self._subdir)
#                 parameter reduced 10000 times, throwing an exception

      Log("  OptimizeEagerZero Test: " + path)
      ph.SetPhase("OptimizeEagerZero Test Begin")
      task = self._vdm.OptimizeEagerZeroVirtualDisk(path, self._dc)
      WaitForTask(task, True)
      ph.SetPhase("OptimizeEagerZero Test End")
      self.DeleteSingle(path)


   def TestInflate(self):
      Log("VirtualDiskManager: Inflate test")
      path = self.CreateSingle("InflateTest", "thin")
      Log("  Inflating: " + path)
      task = self._vdm.InflateVirtualDisk(path)
      WaitForTask(task, True)
      self.DeleteSingle(path)

   def TestInsufficientCapacity(self):
      Log("VirtualDiskManager: Insufficient Capacity Test")
      capacity = self.FindDatastore().GetCapacity()
      try:
         path = self.CreateSingle(name="InsufficientCapacity", size=capacity)
         self.DeleteSingle(path)
         raise Exception(" Expected 'NoDiskSpace' Exception not thrown. ");
      except Vim.Fault.NoDiskSpace as e:
         Log("Caught expected exception : " + str(e))
         if str(e.datastore) != self._dsName:  # check for correct datastore
            raise Exception(" Exception datastore: '%s' does not match" \
                            " expectation: '%s'" % \
                            (str(e.datastore),self._dsName));

def main():
   supportedArgs = [
      (["h:", "host="], "localhost", "Host name", "host"),
      (["u:", "user="], "root", "User name", "user"),
      (["p:", "pwd="], "ca$hc0w", "Password", "pwd"),
      (["d:", "ds="], None, "Datastore name", "ds"),
      (["r:", "rdm="], None, "Device path used in rdm creation", "rdm"),
      (["n:", "nas="], None,
              "Nas datastore creation info format:'host:share:dsname'", "nas"),
#     (["s:", "subdir="], "testvdm/", "Subdirectory in selected datastore as "
#                         "possible destination for disks'", "subdir"),
      (["i:", "numiter="], "1", "Number of iterations", "iter") ]

   supportedToggles = [
          (["usage", "help"], False, "Show usage information", "usage"),
          (["cleanup", "c"], True, "Try to cleanup test vms from previous runs",
                                   "cleanup")]

   args = arguments.Arguments(sys.argv, supportedArgs, supportedToggles)
   if args.GetKeyValue("usage") == True:
      args.Usage()
      sys.exit(0)

   # Connect
   si = SmartConnect(host=args.GetKeyValue("host"),
                     user=args.GetKeyValue("user"),
                     pwd=args.GetKeyValue("pwd"))

   Log("Connected to host " + args.GetKeyValue("host"))

   # Process command line
   numiter = int(args.GetKeyValue("iter"))
   doCleanup = args.GetKeyValue("cleanup")
   status = "PASS"

   resultsArray = []

   serviceInstanceContent = si.RetrieveContent()
   vdiskMgr = serviceInstanceContent.GetVirtualDiskManager()

   hostSystem = host.GetHostSystem(si)
   hostConfigManager = hostSystem.GetConfigManager()
   global datastoreSystem
   datastoreSystem = hostConfigManager.GetDatastoreSystem()

   if vdiskMgr == None:
      Log("Virtual Disk Manager not found")
      sys.exit(0)

   for i in range(numiter):
      bigClock = StopWatch()
      try:
         try:
            ph = Phase()

            vdiskMgrTest = VirtualDiskManagerTest(vdiskMgr, args)
            vdiskMgrTest.RunTests()

            ph.SetPhase("Virtual Disk Manager Tests")
            status = "PASS"

         finally:
            bigClock.finish("iteration " + str(i))

      # While debugging, uncomment the line below to see backtraces
      # when an exception occurs.
      except Exception as e:
         Log("Caught exception : " + str(e))
         status = "FAIL"

      Log("TEST RUN COMPLETE: " + status)
      resultsArray.append(status)

   Log("Results for each iteration: ")
   for i in range(len(resultsArray)):
      Log("Iteration " + str(i) + ": " + resultsArray[i])

# Start program
if __name__ == "__main__":
    main()
