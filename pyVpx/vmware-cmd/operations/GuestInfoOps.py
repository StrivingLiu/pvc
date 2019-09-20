from Operation import Operation
from ConfigOps import GetConfig
from Nic import Nic


class SetGuestInfo(Operation):

   usage = '<variable> <value>'

   def DoIt(self, host, vm, variable, value):
      """
      This operation can set arbitrary key/value pairs for a VM
      running VMware Tools.

      This data is stored in the config.extraConfig VMODL property.

      Examples:

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getguestinfo marc
      getguestinfo(marc) = 101

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' setguestinfo marc 102
      setguestinfo(marc, 102) = success

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getguestinfo marc
      getguestinfo(marc) = 102

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getguestinfo abc
      None

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' setguestinfo abc def
      setguestinfo(abc, def) = success

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getguestinfo abc
      getguestinfo(abc) = def
      """

      vm = Operation.GetVm(host, vm)

      extraConfig = vm.GetExtraConfig()
      extraConfig['guestinfo.%s' % variable] = value

      return extraConfig.Save()


class GetGuestInfo(Operation):

   usage = '<variable>'

   def DoIt(self, host, vm, variable=None):
      """
      Gets information about the vm's guest operating system, such as
      the guest's IP address, or gets the value of a key/value pair
      that was set by the user (e.g.: using the"setguestinfo" operation).

      Examples:

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getguestinfo ip
      getguestinfo(ip) = 10.17.40.249

      (More examples in the docs for "setguestinfo").
      """

      vm = Operation.GetVm(host, vm)

      return GetConfig().DoIt(host, vm, 'guestinfo.%s' % variable)


class ListGuestNics(Operation):

   hidden = True
   
   def DoIt(self, host, vm):
      """
      """

      nics = GetConfig().DoIt(host, vm, 'guest.net')
      if nics is not None:
         return map(Nic, nics)
      else:
         return None
