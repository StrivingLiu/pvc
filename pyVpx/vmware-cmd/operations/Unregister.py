import sys
from Operation import Operation


class Unregister(Operation):
   """
   Unregister a virtual machine from the host. 
   To unregister misconfigured VM use path shown by listvms operation.
   """

   usage = '<config_file_path>'

   def DoIt(self, host, name):
      """
      Example:

      $ ./vmware-cmd2 -H pivot02 -U root -P password "[] /vmfs/volumes/457d7a7c-01488e38-480b-003048322058/test1/test1.vmx" unregister

      $ ./vmware-cmd2 -H pivot2 -U root -P password test1 unregister

      """

      vm = Operation.GetVmEx(host, name)
      if (vm == None):
         sys.stderr.write(
            'VM \'%s\' can\'t be found neither by summary name '
            'nor by filename\n' % name)
         return


      return host.UnregisterVm(vm)
