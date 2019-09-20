from Device import Device, DeviceId
from Utils import rec_getattr, memoize
from Task import Task
import pyVmomi


class Vm(object):
   """
   Wraps a VirtualMachine ManagedObject and adds some methods and
   properties for convenience.
   """

   def __init__(self, host, managedObject):
      if managedObject is None:
         raise pyVmomi.vim.fault.NotFound(
            message='Virtual machine managed object not found')

      self.host = host
      self.managedObject = managedObject
      self.type = self.__class__.__name__
      if managedObject:
         config = managedObject.summary.config
         self.name = config.name
         self.dsPath = host.GetDsPathFromLocalPath(config.vmPathName)

   @property
   def localPath(self):
      return self.host.GetLocalPathFromDsPath(self.dsPath)

   @property
   @memoize
   def powerState(self):
      """
      if not hasattr(self, '_powerState'):
         self._powerState = self.GetPowerState()

      return self._powerState
      """
      return self.GetPowerState()

   def GetPowerState(self):
      if self.managedObject.runtime.question: return 'stuck'

      powerState = self.managedObject.runtime.powerState

      powerStateMap = {
         'poweredOn':    'on',
         'poweredOff':   'off',
         }

      if powerStateMap.has_key(powerState):
         return powerStateMap[powerState]
      else:
         return powerState

   @property
   def questionPending(self):
      return ('Question pending', '') \
             [self.managedObject.runtime.question is None]

   @property
   def moId(self):
      moStr = str(self.managedObject) # e.g.: 'vim.VirtualMachine:(\d+)'
      return int(moStr[moStr.index(':') + 1:-1])

   @property
   def mobUrl(self):
      return 'https://%s/mob/?moid=%d' % (self.host.hostname, self.moId)

   def __str__(self):
      return self.name

   def __repr__(self):
      return '%s(%s)' % (type(self).__name__,
                         self.managedObject.__repr__())

   @property
   def ConfigSpec(self):
      return pyVmomi.Vim.vm.ConfigSpec

   @property
   def VirtualDeviceSpec(self):
      return pyVmomi.Vim.Vm.Device.VirtualDeviceSpec

   def YieldAllDevices(self):
      """
      A generator that yields all of the devices that belong to the
      virtual machine.
      """

      for deviceManagedObject in self.managedObject.config.hardware.device:
         yield Device(vm=self, managedObject=deviceManagedObject)

   def GetAllDevices(self):
      """
      Calls YieldAllDevices and materializes the generator into a list.
      """

      return list(self.YieldAllDevices())

   def GetDevice(self, arg):
      """
      Get a single device by creating a DeviceId from the arg and
      using it to find a matching device.
      """

      if not arg: return None

      deviceSpec = DeviceId(arg)

      for device in self.YieldAllDevices():
         if deviceSpec.Matches(device): return device

   def __getattr__(self, name):
      """ Delegate unknown attributes/methods to the managed object. """

      value = rec_getattr(self.managedObject, name)

      if value:
         return value
      else:
         return getattr(self.managedObject, name)

   def GetExtraConfig(self):
      return self.ExtraConfig(optionValueList=self.config.extraConfig, vm=self)

   class ExtraConfig(dict):

      def __init__(self, optionValueList, vm):
         dict.__init__(self,
                       [ (optionValue.key, optionValue.value)
                         for optionValue in optionValueList ])
         self.vm = vm

      def GetOptionValueList(self):
         optionValueList = []

         for key, value in self.items():
            optionValue = pyVmomi.Vim.Option.OptionValue()
            optionValue.SetKey(key)
            optionValue.SetValue(value)
            optionValueList.append(optionValue)

         return optionValueList

      def Save(self):
         configSpec = self.vm.ConfigSpec()
         configSpec.extraConfig = self.GetOptionValueList()
         return self.vm.Reconfigure(configSpec)
