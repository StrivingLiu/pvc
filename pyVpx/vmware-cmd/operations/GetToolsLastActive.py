from Operation import Operation


class GetToolsLastActive(Operation):

   usage = ''

   def DoIt(self, host, vm):
      """
      Example:

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' gettoolslastactive
      gettoolslastactive() = 1
      """

      vm = Operation.GetVm(host, vm)

      status = vm.GetGuestHeartbeatStatus()

      return self.FakeLastActiveCountFromHeartbeatColor(status)

   @classmethod
   def FakeLastActiveCountFromHeartbeatColor(cls, heartbeatColor):
      """
      This mapping came from the VMControlSoapVMUpdateHealth function
      in bora/lib/vmcontrol/vmcontrolSoapUtil.c
      """

      return cls.heartbeatColorToLastActiveCount[heartbeatColor]

   heartbeatColorToLastActiveCount = {
      'gray'    :   0,
      'green'   :   1,
      'yellow'  :   5,
      'red'     : 100,
      }
