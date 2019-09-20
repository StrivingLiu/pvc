from Operation import Operation


class GetConfigFile(Operation):

   usage = ''

   def DoIt(self, host, vm):
      """
      Example:

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfigfile
      getconfigfile() = /vmfs/volumes/44ee4eb7-28601011-5305-000e0c6dbc76/VirtualCenter 2.5 VM/VirtualCenter 2.5 VM.vmx
      """

      vm = Operation.GetVm(host, vm)

      return vm.localPath
