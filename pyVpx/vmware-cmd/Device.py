from Utils import rec_getattr


class DeviceId(object):
   """
   Encapsulates referring to a device by:

    * An integer VMODL key
    * An id string like "scsi0:0" or "floppy0"

   and provides a Matches method
   """

   def __init__(self, arg0):
      if isinstance(arg0, int) or \
         (isinstance(arg0, basestring) and arg0.isdigit()):
         self.Matches = lambda device: int(arg0) == device.key
      else:
         self.Matches = lambda device: arg0 == device.idString


class Device(object):
   """
   Wraps a Device ManagedObject and adds some methods and
   properties for convenience.
   """

   def __init__(self, vm, managedObject):
      self.vm = vm
      self.managedObject = managedObject
      self._controller = None
      self.ex = self.managedObject.connectable
      self.type = self.__class__.__name__

   def SetConnected(self, arg):
      return self.managedObject.GetConnectable().SetConnected(arg)

   def Save(self):
      deviceSpecType = self.vm.VirtualDeviceSpec
      deviceSpec = deviceSpecType()
      deviceSpec.device = self.managedObject
      deviceSpec.operation = deviceSpecType.Operation.edit

      configSpec = self.vm.ConfigSpec()
      configSpec.deviceChange.append(deviceSpec)

      return self.vm.Reconfigure(configSpec)

   @property
   def label(self):
      return self.managedObject.deviceInfo.label.rstrip()

   @property
   def dataObjectType(self):
      """ e.g.: "VirtualFloppy", "VirtualLsiLogicController", etc. """

      return self.managedObject.__class__.__name__.split('.')[-1]

   @property
   def idString(self):
      """ e.g.: "scsi0:0", "floppy0", etc. """

      interfaceType = self.interfaceType

      if interfaceType == 'floppy':
         return '%s%d' % (interfaceType, self.unitNumber)
# <todo>
#       How do we get the string to an ethernet or serial device?
#
#       elif interfaceType == 'ethernet' or \
#            interfaceType == 'serial':
#          return '%s%d' % (interfaceType, unitNumber - 1)
# </todo>
      elif interfaceType in ['scsi', 'ide'] and \
           self.busNumber is not None and self.unitNumber is not None:
         return '%s%s:%s' % (interfaceType, self.busNumber, self.unitNumber)
      else:
         return None

   @property
   def controller(self):
      if not self._controller:
         self._controller = self.vm.GetDevice(self.controllerKey)

      return self._controller

   @property
   def busNumber(self):
      if hasattr(self.managedObject, 'busNumber'):
         return self.managedObject.busNumber
      else:
         if self.controller: return self.controller.busNumber
         else: return None

   @property
   def interfaceType(self):
      dataObjectTypes = self.__class__.dataObjectTypes

      for interfaceType, objectTypes in dataObjectTypes.items():
         if self.dataObjectType in objectTypes:
            return interfaceType

      if self.controller:
         for interfaceType, objectTypes in dataObjectTypes.items():
            if self.controller.dataObjectType in objectTypes:
               return interfaceType

   @property
   def clientDevice(self):
      backingType = type(self.managedObject.backing).__name__.split('.')[-1]
      return backingType in ['RemotePassthroughBackingInfo',
                             'RemoteAtapiBackingInfo',
                             'RemoteDeviceBackingInfo',
                             'FloppyRemoteDeviceBackingInfo']

   @property
   def fileType(self):
      return self.deviceType

   @property
   def deviceType(self):
      backingType = type(self.managedObject.backing).__name__.split('.')[-1]
      if backingType in ['RemotePassthroughBackingInfo',
                         'PassthroughBackingInfo',
                         'RemoteAtapiBackingInfo',
                         'AtapiBackingInfo']:
         devType = type(self.managedObject.backing).__name__.split('.')[-2]
         if devType == 'VirtualCdrom':
            return 'cdrom-raw'
      elif backingType == 'IsoBackingInfo':
         return 'cdrom-image'
      elif backingType in ['RemoteDeviceBackingInfo',
                           'FloppyDeviceBackingInfo',
                           'DeviceDeviceBackingInfo']:
         return 'device'
      elif backingType in ['ImageBackingInfo',
                           'FileBackingInfo']:
         return 'file'
      elif backingType in ['FlatVer1BackingInfo',
                           'FlatVer2BackingInfo',
                           'SparseVer1BackingInfo',
                           'SparseVer2BackingInfo']:
         return 'disk'
      elif backingType in ['PartitionedRawDiskVer2BackingInfo',
                           'RawDiskMappingVer1BackingInfo',
                           'RawDiskVer2BackingInfo']:
         return 'raw'

      return backingType

   @property
   def device(self):
      return self.managedObject.backing.deviceName

   @property
   def present(self):
      return 1

   @property
   def fileName(self):
      return self.managedObject.backing.fileName

   @property
   def mode(self):
      return self.managedObject.backing.diskMode

   @property
   def startConnected(self):
      return int(self.managedObject.connectable.startConnected)

   def __getattr__(self, name):
      return rec_getattr(self.managedObject, name)

   def __str__(self):
      return 'device[%d]' % self.managedObject.key

   def __repr__(self):
      return '%s(%s, %s)' % (self.__class__.__name__,
                             self.vm,
                             self.managedObject)

   dataObjectTypes = {
      'floppy':    ['VirtualFloppy'],
      'serial':    ['VirtualSerialPort',
                    'VirtualSIOController'],
      'ide':       ['VirtualIDEController'],
      'scsi':      ['VirtualLsiLogicController',
                    'VirtualBusLogicController'],
      'ps2':       ['VirtualPS2Controller'],
      'pci':       ['VirtualPCIController'],
      'ethernet':  ['VirtualE1000',
                    'VirtualPCNet32',
                    'VirtualVmxnet',
                    'VirtualVmxnet2',
                    'VirtualVmxnet3',
                    'VirtualVmxnet3Vrdma']}
