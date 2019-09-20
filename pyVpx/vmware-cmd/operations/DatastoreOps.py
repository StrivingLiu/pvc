from Operation import Operation
import pyVmomi


class ListDatastores(Operation):
   """
   List the datastores of a host.
   """

   hidden = True
   usage = ''

   def DoIt(self, host):
      """
      Example:

      $ ./vmware-cmd2 -H pivot02 listdatastores
      storage1    /vmfs/volumes/457d7a7c-01488e38-480b-003048322058    6851395584
      """

      return host.hostSystem.datastore


class CreateNasDatastore(Operation):
   """
   Mount a NAS (e.g.: NFS or CIFS) datastore.
   """

   hidden = True
   
   def DoIt(self,
            host,
            localPath,
            remoteHost,
            remotePath,
            accessMode='readWrite'):
      """
      Example:

      $ ./vmware-cmd -H pioneer-131 createnasdatastore pa-home pa-home.eng.vmware.com /home4
      createnasdatastore(pa-home, pa-home.eng.vmware.com, /home4) = Created NAS datastore: pa-home at /vmfs/volumes/aea83165-67ecf0a4.

      $ ./vmware-cmd -H pioneer-131 listdatastores
      storage1       /vmfs/volumes/44ee4eb7-28601011-5305-000e0c6dbc76    1956642816
      exit14_home    /vmfs/volumes/7fc57c6d-1467d110                      1129813446656
      pa-home        /vmfs/volumes/aea83165-67ecf0a4                      635146485760
      """

      spec = pyVmomi.vim.host.NasVolume.Specification()
      spec.localPath = localPath
      spec.remoteHost = remoteHost
      spec.remotePath = remotePath
      spec.accessMode = accessMode

      datastore = host.datastoreSystem.CreateNasDatastore(spec)
      if datastore and datastore.summary.accessible:
         return('Created NAS datastore: %s at %s.'
               % (datastore.summary.name, datastore.summary.url))


class RemoveDatastore(Operation):
   """
   Remove a datastore with the specified name.
   """

   hidden = True
   
   def DoIt(self, host, datastoreName):
      """
      Example:

      $ ./vmware-cmd -H pioneer-131 removedatastore pa-home
      removedatastore(pa-home) = Removed datastore: pa-home
      """

      datastore = host.GetDatastoreByName(datastoreName)
      datastore = host.datastoreSystem.RemoveDatastore(datastore)

      return('Removed datastore: %s' % datastoreName)
