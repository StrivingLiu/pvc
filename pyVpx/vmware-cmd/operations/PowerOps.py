from Operation import Operation


class PowerOp(Operation):
   """
   Base class for other power operations.
   """

   # PR423319 
   usage = '[soft|hard|trysoft]'

   def DoIt(self, host, vm, powerOpMode='soft'):
      vm = Operation.GetVm(host, vm)

      if powerOpMode == 'soft':
         return self.SoftPowerOp(vm)
      elif powerOpMode == 'trysoft':
         try:
            return self.SoftPowerOp(vm)
         except:
            if self.HardPowerOp != self.SoftPowerOp:
               return self.HardPowerOp(vm)
            else:
               raise
      elif powerOpMode == 'hard':
         return self.HardPowerOp(vm)
      else:
         raise RuntimeError('Invalid power operation mode: %s' % powerOpMode)


class Start(PowerOp):
   """
   Power on a virtual machine.

   Note that there's no difference between soft and hard power-on
   operations so the SoftPowerOp and HardPowerOp methods do the same
   thing.
   """

   def CommonPowerOp(self, vm): return vm.PowerOn()
   SoftPowerOp = CommonPowerOp
   HardPowerOp = CommonPowerOp


class Stop(PowerOp):

   def SoftPowerOp(self, vm):   return vm.ShutdownGuest()
   def HardPowerOp(self, vm):   return vm.PowerOff()


class Reset(PowerOp):

   def SoftPowerOp(self, vm):   return vm.RebootGuest()
   def HardPowerOp(self, vm):   return vm.Reset()


class Suspend(PowerOp):

   def SoftPowerOp(self, vm):   return vm.StandbyGuest()
   def HardPowerOp(self, vm):   return vm.Suspend()
