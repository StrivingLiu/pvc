from pyVmomi import vim, Vmodl

VERSION = 'pvc-1.0'

MANAGED_ENTITIES = {
   'computeResource' : vim.ComputeResource,
   'datacenter' : vim.Datacenter,
   'datastore' : vim.Datastore,
   'virtualSwitch' : vim.DistributedVirtualSwitch,
   'folder' : vim.Folder,
   'hostsystem' : vim.HostSystem,
   'network' : vim.Network,
   'resourcePool' : vim.ResourcePool,
   'virtualMachine' : vim.VirtualMachine
}

class InputMode:
   NORMAL = 1
   DEBUG = 2