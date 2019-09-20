import sys
from TaskStub import Task
from Struct import Struct
from Mock import Mock


class VimFault(Exception):
   pass


VimFault.__module__ = 'pyVmomi.vim.fault'

class NotFound(VimFault): pass

class InvalidPowerState(VimFault):

   def __init__(self):
      VimFault.__init__(self)


class ToolsUnavailable(VimFault):

   def __init__(self):
      VimFault.__init__(self)


def RaiseInvalidPowerState(powerState):
   raise vim.fault.InvalidPowerState(msg='The attempted operation cannot be performed in the ' + \
                                     'current state (%s).' % powerState)

def RaiseToolsUnavailable():
   raise vim.fault.ToolsUnavailable(msg='Operation failed since VMware tools are not running in this virtual machine.')

InvalidPowerState.__module__ = 'pyVmomi.vim.fault'
ToolsUnavailable.__module__ = 'pyVmomi.vim.fault'
NotFound.__module__ = 'pyVmomi.vim.fault'

try:
   import pyVmomi
except:
   pyVmomi = Struct(
      vim=Struct(
         fault=Struct(
            InvalidPowerState=InvalidPowerState,
            ToolsUnavailable=ToolsUnavailable,
            NotFound=NotFound,
         )
      )
   )

vim = pyVmomi.vim


class Vm(Mock):

   def __init__(self,
                name,
                host=None,
                powerState='poweredOff',
                powerOpSleepSeconds=1,
                *args,
                **kwargs):
      Mock.__init__(self, *args, **kwargs)

      self.name = name
      self.host = host
      self.powerState = powerState
      self.powerOpSleepSeconds = powerOpSleepSeconds
      self.config = Struct()
      self.guest = Struct()
      self.extraConfig = {}
      self.toolsInstalled = True

      # Take keyword arg values passed in and use them to set object attributes
      self.__dict__.update(kwargs)

   @property
   def dsPath(self):
      return '[fake_datastore] %s.vmx' % self.name

   def GetExtraConfig(self):
      return self.extraConfig

   def GetDevice(self, arg):
      ## @todo Not implemented yet
      return None

   def GetAllDevices(self):
      class Device(Struct):
         pass
      return [
         Device(
            key='key',
            idString='idString',
            deviceInfo=Struct(
               label='label',
               summary='summary',
            ),
            connectable=Struct(
               connected=False,
            ),
         ),
      ]

   def DoPowerOp(self,
                 taskName,
                 newPowerState,
                 invalidInitialStates,
                 toolsRequired=False):
      if self.powerState in invalidInitialStates:
         RaiseInvalidPowerState(self.powerState)

      if toolsRequired and not self.toolsInstalled:
         RaiseToolsUnavailable()

      def _func():
         self.powerState = newPowerState

      return Task(taskName=taskName,
                  sleepSeconds=self.powerOpSleepSeconds,
                  func=_func,
                  returnValue='success')

   def PowerOn(self):
      return self.DoPowerOp(taskName='VirtualMachine.powerOn',
                            newPowerState='on',
                            invalidInitialStates=('on'))

   def ShutdownGuest(self):
      return self.DoPowerOp(taskName='VirtualMachine.shutdownGuest',
                            newPowerState='off',
                            invalidInitialStates=('off'),
                            toolsRequired=True)

   def PowerOff(self):
      return self.DoPowerOp(taskName='VirtualMachine.powerOff',
                            newPowerState='off',
                            invalidInitialStates=('off'))

   def RebootGuest(self):
      return self.DoPowerOp(taskName='VirtualMachine.rebootGuest',
                            newPowerState='on',
                            invalidInitialStates=('off', 'suspended'),
                            toolsRequired=True)

   def Reset(self):
      return self.DoPowerOp(taskName='VirtualMachine.reset',
                            newPowerState='on',
                            invalidInitialStates=('off', 'suspended'))

   def StandbyGuest(self):
      return self.DoPowerOp(taskName='VirtualMachine.standbyGuest',
                            newPowerState='suspended',
                            invalidInitialStates=('off', 'suspended'),
                            toolsRequired=True)

   def Suspend(self):
      return self.DoPowerOp(taskName='VirtualMachine.suspend',
                            newPowerState='suspended',
                            invalidInitialStates=('off', 'suspended'))

   def __eq__(self, other):
      return self.name == other.name
