from Operation import Operation


class DeleteVm(Operation):
   """
   Delete a virtual machine.
   """

   hidden = True
   
   def DoIt(self, host, vm):
      """
      Example:

      $ ./vmware-cmd2 -H sdk167 deletevm mabramow-test3
      ???
      """

      vm = Operation.GetVm(host, vm)

      return vm.Destroy()
