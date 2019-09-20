from Operation import Operation


class SetConfig(Operation):

   usage = '<variable> <value>'
   notes = '(Implemented only for items in extraConfig)'
   hidden = True

   def DoIt(self, host, vm, variable, value):
      """
      @todo Currently, this is only handling config items that map to
      extraConfig so this is not complete. It needs to handle config
      items that map to specialized VMODL properties.

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig annotation
      getconfig(annotation) = 'jhu VC 2.5 VM'

      [Bugs]

      ### ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' setconfig annotation xyz
      None

      ### ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig annotation
      getconfig(annotation) = 'jhu VC 2.5 VM'

      @todo Cannot do setconfig on annotation
      """

      vm = Operation.GetVm(host, vm)

      extraConfig = vm.GetExtraConfig()
      if variable in extraConfig:
         extraConfig[variable] = value
         return extraConfig.Save()


from Utils import rec_getattr

class GetConfig(Operation):

   usage = '<variable>'

   def DoIt(self, host, vm, variable):
      """
      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig floppy0.present
      getconfig(floppy0.present) = 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig floppy0.fileType
      getconfig(floppy0.fileType) = file

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig floppy0.fileName
      getconfig(floppy0.fileName) = [] /vmimages/floppies/vmscsi-1.2.0.2.flp

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig floppy0.clientDevice
      getconfig(floppy0.clientDevice) = 0

      $ ./vmware-cmd2 -H pivot02 mabramow-esx-1-cos getconfig floppy0.startConnected
      getconfig(floppy0.startConnected) = 0

      $ ./vmware-cmd2 -H pivot02 mabramow-esx-1-cos getconfig floppy0.ex.connected
      getconfig(floppy0.ex.connected) = 0

      $ ./vmware-cmd2 -H pivot02 mabramow-esx-1-cos getconfig floppy0.connectable.connected
      getconfig(floppy0.connectable.connected) = 0

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig floppy0.deviceInfo.label
      getconfig(floppy0.deviceInfo.label) = Floppy Drive 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig floppy0.key
      getconfig(floppy0.key) = 8000

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig floppy0
      (vim.vm.device.VirtualFloppy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         key = 8000,
         ...
      }

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig ide0:0.present
      getconfig(ide0:0.present) = 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig ide0:0.clientDevice
      getconfig(ide0:0.clientDevice) = 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig ide0:0.deviceType
      getconfig(ide0:0.deviceType) = cdrom-raw

      $ ./vmware-cmd2 -H pivot02 mabramow-esx-1-cos getconfig ide0:0.deviceType
      getconfig(ide0:0.deviceType) = cdrom-image

      $ ./vmware-cmd2 -H pivot02 mabramow-esx-1-cos getconfig ide0:0.fileName
      getconfig(ide0:0.fileName) = [storage1] iso/mabramow/beta/esx-kl.iso

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig ide0:0.startConnected
      getconfig(ide0:0.startConnected) = 1

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig ide0:0.ex.connected
      getconfig(ide0:0.ex.connected) = 1

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig ide0:0.connectable.connected
      getconfig(ide0:0.connectable.connected) = 1

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig ide0:0.deviceInfo.label
      getconfig(ide0:0.deviceInfo.label) = CD/DVD Drive 1

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig ide0:0.key
      getconfig(ide0:0.key) = 3000

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig ide0:0
      (vim.vm.device.VirtualCdrom) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         key = 3000,
         ...
      }

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig scsi0:0.present
      getconfig(scsi0:0.present) = 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig scsi0:0.clientDevice
      getconfig(scsi0:0.clientDevice) = 0

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig scsi0:0.deviceType
      getconfig(scsi0:0.deviceType) = disk

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig scsi0:0.fileName
      getconfig(scsi0:0.fileName) = [storage1] VirtualCenter 2.5 VM/VirtualCenter 2.5 VM.vmdk

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig scsi0:0.mode
      getconfig(scsi0:0.mode) = persistent

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig scsi0:0.key
      getconfig(scsi0:0.key) = 2000

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig extraConfig
      getconfig(extraConfig) = (vim.option.OptionValue) [
         (vim.option.OptionValue) {
               dynamicType = <unset>,
               dynamicProperty = (vmodl.DynamicProperty) [],
               key = 'checkpoint.vmState.readOnly',
               value = 'FALSE'
         }, ...
      ]

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig guestinfo.ip
      getconfig(guestinfo.ip) = 10.17.40.249

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig memSize
      getconfig(memSize) = 4

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig config.version
      getconfig(config.version) = vmx-04

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig displayName
      getconfig(displayName) = mabramow-test1

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig uuid.location
      getconfig(uuid.location) = 564d7e1c-c8f7-b7cf-29a1-dd05bc561c03

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig uuid.bios
      getconfig(uuid.bios) = 564d7e1c-c8f7-b7cf-29a1-dd05bc561c03

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig annotation
      getconfig(annotation) = 'jhu VC 2.5 VM'

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig workingDir
      getconfig(workingDir) = [storage1] VirtualCenter 2.5 VM

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig redoLogDir
      getconfig(redoLogDir) = [storage1] VirtualCenter 2.5 VM

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig suspend.directory
      getconfig(suspend.directory) = [storage1] VirtualCenter 2.5 VM

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig disable_acceleration
      getconfig(disable_acceleration) = 0

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig debug
      getconfig(debug) = 0

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig logging
      getconfig(logging) = 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig net.toe
      getconfig(net.toe) = 0

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig toolScripts.afterPowerOn
      getconfig(toolScripts.afterPowerOn) = 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig toolScripts.afterResume
      getconfig(toolScripts.afterResume) = 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig toolScripts.beforePowerOff
      getconfig(toolScripts.beforePowerOff) = 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig toolScripts.beforeSuspend
      getconfig(toolScripts.beforeSuspend) = 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig powerType.powerOff
      getconfig(powerType.powerOff) = preset

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig powerType.suspend
      getconfig(powerType.suspend) = preset

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig powerType.reset
      getconfig(powerType.reset) = preset

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig numvcpus
      getconfig(numvcpus) = 2

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 getconfig config
      ... lots of output ...
      """

      vm = Operation.GetVm(host, vm)

      variableComponents = variable.split('.', 1)
      device = vm.GetDevice(variableComponents[0])
      if device:
         if len(variableComponents) > 1:
            return rec_getattr(device, variableComponents[1])
         else:
            return device


      value = vm.GetExtraConfig().get(variable, None)
      if value: return value

      return rec_getattr(vm, self.GetVmodlProperty(variable))

   @classmethod
   def GetVmodlProperty(cls, variable):
      """
      Either translates variable to a VMODL property name, or returns
      variable as-is.
      """

      return cls.mappings.get(variable.lower(), variable)

   mappings = { 'guestinfo.ip'                : 'guest.ipAddress',
                'memSize'                     : 'config.hardware.memoryMB',
                'guestOs'                     : 'config.guestId',
                'displayName'                 : 'config.name',
                'uuid.location'               : 'config.locationId',
                'uuid.bios'                   : 'config.uuid',
                'annotation'                  : 'config.annotation',
                'workingDir'                  : 'config.files.snapshotDirectory',
                'redoLogDir'                  : 'config.files.snapshotDirectory',
                'suspend.directory'           : 'config.files.suspendDirectory',
                'disable_acceleration'        : 'config.flags.disableAcceleration',
                'debug'                       : 'config.flags.runWithDebugInfo',
                'logging'                     : 'config.flags.enableLogging',
                'net.toe'                     : 'config.flags.useToe',
                'numvcpus'                    : 'config.hardware.numCPU',
                'toolScripts.afterPowerOn'    : 'config.tools.afterPowerOn',
                'toolScripts.afterResume'     : 'config.tools.afterResume',
                'toolScripts.beforePowerOff'  : 'config.tools.beforeGuestShutdown',
                'toolScripts.beforeSuspend'   : 'config.tools.beforeGuestStandby',
                'powerType.powerOff'          : 'config.defaultPowerOps.powerOffType',
                'powerType.suspend'           : 'config.defaultPowerOps.suspendType',
                'powerType.reset'             : 'config.defaultPowerOps.resetType',
                }

   # Convert mappings to have lowercase keys so we can do case-insensitive match
   mappings = dict([(key.lower(), val) for (key, val) in mappings.items()])
