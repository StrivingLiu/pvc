from Operation import Operation


class ListVms(Operation):
   """
   List the virtual machines managed by the host.
   """

   usage = ''

   def DoIt(self, host):
      """
      Example:

      $ ./vmware-cmd2 -H sdk167 listvms
      /vmfs/volumes/480f5047-89477104-8187-00151737da23/win2kvm2_sdk167/win2kvm2_sdk167.vmx
      /vmfs/volumes/480f5047-89477104-8187-00151737da23/win2kvm1_sdk167/win2kvm1_sdk167.vmx
      """
      
      return host.GetVms()
