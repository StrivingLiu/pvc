# Copyright 2016 VMware, Inc. All rights reserved.  -- VMware Confidential
# pyHbr.pretty.py
#
# Python wrappers for pretty printing various hbrsrv VMODL structures
#
# Not meant to be invoked directly.  Shared utility code for other hbrsrv
# wrappers.
#

from pyVmomi import Hbr
from pyVmomi import Vmodl # for the exceptions

indentlevel = 0

class IndentCtx(object):
   """
   Context manager useful for indenting.
   """
   def __enter__(self):
      global indentlevel # make thread private someday
      indentlevel = indentlevel + 1

   def __exit__(self, exc_type, exc_val, exc_tb):
      global indentlevel # make thread private someday
      indentlevel = indentlevel - 1
      return (exc_type is None)


class IndentAll(object):
   """
   Decorator for tagging pretty printer functions.  Automagic pretty
   indenting.  (Look for @IndentAll).
   """
   def __init__(self, f):
      self.f = f
   def __call__(self, *args):
      with IndentCtx():
         self.f(*args)

def PrettyPrint(*args):
   """
   Pretty-print wrapper for 'print', works with the glovel indentlevel
   controlled through IndentCtx and @IndentAll.
   """
   global indentlevel

   # Compute and print indentation
   indent = ""
   for i in range(indentlevel):
      indent += "   "
   print indent,

   # Print all the arguments, with a space between
   for a in args:
      print a,
   print


###
### Pretty print routines for various HBR VMODL types
###


def PrintIdent(name, i):
   PrettyPrint(name, i.id, "/vmfs/volumes/{0}/{1}".format(
                                             i.location.datastoreUUID,
                                             i.location.pathname))


@IndentAll
def PrintImageDisk(gr, img, vm, disk):
   """
   An image disk is really just the identity (id, datastore and path)
   """
   PrintIdent("Disk Image", disk.diskIdent)


@IndentAll
def PrintConfigFile(gr, cfg):
   """
   An image config file is the type and base filename
   """
   PrettyPrint("cfg:", cfg.type, cfg.baseFileName)


@IndentAll
def PrintImageVM(g, i, vm):
   #print g, i, vm

   PrintIdent("VM Image", vm.virtualMachineIdent)
   for disk in vm.disks:
      PrintImageDisk(g, i, vm, disk)
   for cfg in vm.configFiles:
      PrintConfigFile(g, cfg)


@IndentAll
def PrintImage(g, i):
   PrettyPrint("Group Image", i)
   PrettyPrint("Timestamp:", i.GetTimestamp())
   PrettyPrint("InstanceId:", i.GetInstanceId())
   PrettyPrint("IsTestBubble:", i.testBubble)
   PrettyPrint("SnapshotPITImages:", i.snapshotPITImages)
   vms = i.GetVirtualMachines()
   for vm in vms:
      PrintImageVM(g, i, vm)


@IndentAll
def PrintVMInstance(g, vm):
   PrettyPrint("ID:", vm.id)
   cfgs=[]
   for c in vm.configFiles:
      cfgs.append(c)

   PrettyPrint("Quiesced type:", vm.quiescedType)
   PrettyPrint("Config files:", cfgs)
   PrettyPrint("Disk Instances:")
   for d in vm.disks:
      PrintIdent("  ", d.id)


def PrintImageOfInstance(g, image):
   if image:
      PrettyPrint("Image:")
      try:
         PrintImage(g, image)
      except Vmodl.Fault.ManagedObjectNotFound:
         PrettyPrint("<!! image %s not found?>" % str(image))
   else:
      PrettyPrint("Image: None")


@IndentAll
def PrintInstanceDetails(g, i):
   try:
      PrettyPrint("Id:", i.GetKey())
      PrettyPrint("Sequence Number:", i.GetSequenceNumber())

      parent = i.GetParentId()
      PrettyPrint("Parent Id:", parent)

      quiesced = i.GetQuiescedType()
      PrettyPrint("Quiesced Type:", quiesced)

      PrettyPrint("snapshot Time:", i.GetSnapshotTimestamp())

      PrettyPrint("RPO Violation:", i.GetRpoViolation())

      iStats = i.GetInstanceStats()
      PrettyPrint("@", iStats.timestamp,
                  "took", iStats.transferBytes, "bytes",
                  "and", iStats.transferSeconds, "seconds")

      instanceEx = g.GetInstanceDataEx(i.GetKey())
      vms = instanceEx.GetVirtualMachines()
      PrettyPrint("VM Instance:")
      for v in vms:
         PrintVMInstance(g, v)

   except Vmodl.Fault.ManagedObjectNotFound:
      PrettyPrint("<Instance %s went stale>" % str(i))


@IndentAll
def PrintInstance(g, i):
   PrettyPrint("Group Instance", i.GetKey())
   # use a different function for the details to indent them
   PrintInstanceDetails(g, i)

def PrintVMDisk(g, vm, disk):
   label = "VM Disk: "
   if disk.GetUnconfigured():
      label = "VM Disk (uncnf):"

   i = disk.GetDiskIdent()
   PrintIdent(label, i)

   with IndentCtx():
      pitStorage = disk.GetPointInTimeStorage()
      PrettyPrint("PIT storage type: ", pitStorage)
      usage = disk.GetDrmInfo()
      PrettyPrint("Space usage of disk: ", usage.spaceRequirement)
      PrettyPrint("Is disk moveable: ", usage.moveable)
      PrettyPrint("Datastores for single host move: ")
      for dsId in usage.datastoresForSingleHostMove:
         PrettyPrint(" /vmfs/volumes/%s" % dsId)

def PrintGroupVM(g, vm):
   i = vm.virtualMachineIdent
   PrintIdent("VM: ", vm.virtualMachineIdent)

   with IndentCtx():
      mdStorage = vm.GetMetadataStorage()
      PrettyPrint("Metadata storage type: ", mdStorage)
      usage = vm.GetDrmInfo()
      PrettyPrint("Space usage of config files: ", usage.spaceRequirement)
      PrettyPrint("Is disk moveable: ", usage.moveable)
      PrettyPrint("Datastores for single host move: ")
      for dsId in usage.datastoresForSingleHostMove:
         PrettyPrint(" /vmfs/volumes/%s" % dsId)

      tasks = vm.GetRecentTasks()
      if len(tasks) == 0:
         PrettyPrint("Recent tasks: None")
      else:
         PrettyPrint("Recent tasks: ")
         for t in tasks:
            with IndentCtx():
               PrettyPrint(t._GetMoId())

      disks = vm.GetDisks()
      for disk in disks:
         PrintVMDisk(g, vm, disk)

def PrintTaskInfo(g, name, task):
   if task:
      PrettyPrint(name, task._GetMoId())
   else:
      PrettyPrint(name, "No ongoing task.");

def PrintGroup(g):
   PrettyPrint("Group: ", g.GetId())

   with IndentCtx():
      rpo = g.GetRepConfig().GetRpo();
      PrettyPrint("RPO: ", rpo);

      state = g.GetState();
      PrettyPrint("State: ", state)

      rpoViolation = g.GetCurrentRpoViolation();
      PrettyPrint("Current RPO Violation: ", rpoViolation);

      err = g.GetLastGroupError();
      PrettyPrint("Last Error: ", err);

      policy = g.GetRepConfig().policy
      PrintRetentionPolicy(policy)

      prunetask = g.GetSyncPruneTask();
      PrintTaskInfo(g, "Prune task:", prunetask)

      image = g.GetActiveImage()
      PrintImageOfInstance(g, image)

      vms = g.GetVms()
      for vm in vms:
         PrintGroupVM(g, vm)

      instances = g.GetLatestInstances()
      if not instances:
         PrettyPrint("All instances:", "None.")
      else:
         PrettyPrint("All instances:")
         for i in instances:
            PrintInstance(g, i)

      if g.latestInstance:
         # Deeply printed above, presumably
         PrettyPrint("Latest instance:", g.latestInstance.GetKey())
      else:
         PrettyPrint("Latest instance:", "None.")

      childMoRefs = g.GetChildGroups()
      PrettyPrint("Children:", childMoRefs)

@IndentAll
def PrintReplicationManager(rm, givenGroup=None):
   PrettyPrint(rm)

   if givenGroup:
      gr = rm.GetReplicationGroup(givenGroup)
      PrintGroup(gr)
   else:
      for g in rm.groups:
         PrintGroup(g)

@IndentAll
def PrintGroupStats(gid, s):
   PrettyPrint("Group stats for groupID", gid)

   PrettyPrint(s)

@IndentAll
def PrintServerStats(sid, s):
   PrettyPrint("Server stats", sid)

   PrettyPrint(s)

@IndentAll
def PrintHostStats(hid, s):
   PrettyPrint("Host stats for hostID", hid)

   PrettyPrint(s)

@IndentAll
def PrintInstanceQueryResult(group, result):
   PrettyPrint("Returned intances for query")
   PrettyPrint("truncated:  ", result.truncated)
   PrettyPrint("total number of instances: ", len(result.instances))

   for instance in result.instances:
      PrintInstanceDetails(group, instance)

def PrintRetentionPolicy(policy):
   if not policy:
      PrettyPrint("Retention policy: <not set>")
   else:
      tiers = policy.tiers
      if not tiers:
         PrettyPrint("Retention policy: <not set>")
      else:
         prettyPolicy = ""
         for tier in tiers:
            prettyTier = "(%d, %d) " % \
                         (tier.GetGranularityMinutes(), tier.GetNumSlots())
            prettyPolicy += prettyTier
         PrettyPrint("Retention policy: ", prettyPolicy)

#eof
