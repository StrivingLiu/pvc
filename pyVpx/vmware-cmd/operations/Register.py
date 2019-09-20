from Operation import Operation


class Register(Operation):
   """
   Register a virtual machine with the host by providing a path to a config file.
   """

   usage = '<config_file_path>'

   def DoIt(self, host, cfgPath):
      """
      Example:

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfigfile
      (Error)

      $ ./vmware-cmd2 -H pivot02 -s register /vmfs/volumes/457d7a7c-01488e38-480b-003048322058/mabramow-test1/mabramow-test1.vmx
      None

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfigfile
      getconfigfile() = /vmfs/volumes/457d7a7c-01488e38-480b-003048322058/mabramow-test1/mabramow-test1.vmx
      """

      return host.RegisterVm(cfgPath)
