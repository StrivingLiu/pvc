from Operation import Operation
from operations.ResourceOps import GetResource


COUNTER_ID_UPTIME = 262144


class GetUptime(Operation):

   usage = ''

   def DoIt(self, host, vm):
      """
      Example:

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getuptime
      getuptime() = 17066128
      """

      vm = Operation.GetVm(host, vm)

      perfManager = host.perfManager

      return GetResource().GetCounterById(perfManager,
                                          entity=vm.managedObject,
                                          instance='',
                                          counterId=COUNTER_ID_UPTIME)
