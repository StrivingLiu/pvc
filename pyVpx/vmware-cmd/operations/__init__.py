import glob, os, os.path, sys

baseDir = os.getenv('VMWARE_CMD_DIR')
for aDir in ('/usr/lib/vmware/vmware-cmd', '.', '..'):
   if baseDir is not None: break
   if os.path.exists('%s/operations' % aDir): baseDir = aDir

moduleFiles = glob.glob('%s/operations/*.py' % baseDir)
for moduleFile in moduleFiles:
   module, _ = os.path.splitext(os.path.basename(moduleFile))
   exec('from %s import *' % module)

serverOpClasses = [
   ListTasks,
   ListDatastores,
   CreateNasDatastore,
   RemoveDatastore,
   ListPerfCounters,
   CreateVm,
   DeleteVm,
   ListVms,
   Register,
   Unregister,
   GetHostPerfCounter,
   GetResource,
   SetResource,
   ]

vmOpClasses = [
   GetState,
   Start,
   Stop,
   Reset,
   Suspend,
   SetConfig,
   GetConfig,
   SetGuestInfo,
   GetGuestInfo,
   GetProductInfo,
   ListDevices,
   ConnectDevice,
   DisconnectDevice,
   GetId,
   GetConfigFile,
   # GetHeartbeat,
   GetUptime,
   GetToolsLastActive,
   SetResource,
   GetResource,
   HasSnapshot,
   ShowSnapshotTree,
   CreateSnapshot,
   RevertSnapshot,
   RemoveSnapshots,
   Answer,
   ListGuestNics,
   ]

globalsDict = dict(globals())
opsDict = dict(
   [(key.lower(), val)
    for key, val in globalsDict.items()
    if hasattr(val, 'DoIt')]
   )

def GetOperationByName(name):
   ## `name` must be a string
   if not hasattr(name, 'endswith'): return None

   opClass = opsDict.get(name, None)

   if opClass:  return opClass()
   else:        return None
