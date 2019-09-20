from Operation import Operation


class GetState(Operation):
   """
   Get the current power state of a virtual machine.
   """

   usage = ''

   def DoIt(self, host, vm):
      """
      Example:

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getstate
      getstate() = off
      """

      vm = Operation.GetVm(host, vm)

      return vm.powerState
