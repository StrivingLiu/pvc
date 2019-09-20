import time

from Operation import Operation


class GetHeartbeat(Operation):

   usage = ''

   """
   def DoIt(self, host, vm):
      # Note that this returns a color whereas the Perl-based
      # vmware-cmd returned a number
      return vm.GetGuestHeartbeatStatus()
   """

   def DoIt(self, host, vm):
      """
      Example:

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getheartbeat
      332
      """

      vm = Operation.GetVm(host, vm)

      status = vm.GetGuestHeartbeatStatus()

      return self.FakeHeartbeatTimeFromStatus(vm, status)

   def FakeHeartbeatTimeFromStatus(self, vm, status):
      """
      This mapping came from the VMControlSoapVMUpdateHealth function
      in bora/lib/vmcontrol/vmcontrolSoapUtil.c:

      if (vm->lastGuestStatusChecked == 0) {
         vm->heartbeat = HEARTBEAT_START + (now/1000000 % 1000);
      } else if (status == vim2__ManagedEntityStatus__yellow ||
                 status == vim2__ManagedEntityStatus__green) {
         divider = (status == vim2__ManagedEntityStatus__yellow) ? 5 : 1;
         vm->heartbeat += MAX(1, (now - vm->lastGuestStatusChecked)/(1000000*divider));
      }
      """

      HEARTBEAT_START = 10
      now = int(time.time() * 1000000)

      #print('vm.lastGuestStatusChecked = %s' % vm.lastGuestStatusChecked)

      if not hasattr(vm, 'lastGuestStatusChecked') or \
         not vm.lastGuestStatusChecked:
         vm.heartbeat = HEARTBEAT_START + (now/1000000 % 1000)
      elif status == 'yellow' or status == 'green':
         if status == 'yellow': divider = 5
         else: divider = 1
         vm.heartbeat = max(1,
                            (now - vm.lastGuestStatusChecked) /
                            (1000000 * divider))

      return vm.heartbeat
