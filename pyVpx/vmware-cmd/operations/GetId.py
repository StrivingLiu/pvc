from Operation import Operation


class GetId(Operation):
   """
   Get the moId of a virtual machine.
   """

   usage = ''

   def DoIt(self, host, vm):
      """
      Examples:

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getid
      getid() = 4560

      $ ./vmware-cmd2 -q -H pivot02 mabramow-test1 getid
      4560

      $ ./vmware-cmd2
      ...
        VM Operations:
      ...
          ./vmware-cmd2 <cfg> getid
      ...
      """

      vm = Operation.GetVm(host, vm)

      return vm.moId
