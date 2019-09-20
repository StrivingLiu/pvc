import Tree
import optparse
from Operation import Operation
from Formatter import FormatOptions
from Utils import rec_getattr


class ListDevices(Operation):

   hidden = True
   usage = ''

   def _GetOptionParser(self):
      """
      Return an optparse.OptionParser.
      """

      optionParser = optparse.OptionParser()
      optionParser.add_option("--attributes",
                              dest="attrs", metavar="ATTRIBUTES",
                              default="label",
                              help="Attributes to output")
      optionParser.add_option('--display-type', '-d',
                              dest='displayType', default='list',
                              type='choice', choices=['list', 'tree'],
                              help='Display type: {"list", "tree"}')
      optionParser.add_option('--no-vt100-chars',
                              action='store_false', dest='useVt100Chars',
                              default=True,
                              help='Use vt100 line-drawing characters ' +
                                   'to draw the tree view')
      def _error(errorMsg): raise
      optionParser.error = _error
      
      return optionParser

   def DoIt(self, host, vm, *argsTuple):
      options, args = self._GetOptionParser().parse_args(list(argsTuple))
      keywordArgsDict = options.__dict__

      return self._DoIt(host, vm, *args, **keywordArgsDict)

   def _DoIt(self, host, vm,
            attrs='label',
            displayType='list',
            useVt100Chars=True):
      """
      Display virtual devices as a tree or a flat list.

      @param attrs: Attributes to display for each node
      @type  attrs: str (comma-separated values)
      """

      vm = Operation.GetVm(host, vm)
      attrsList = attrs.split(',')

      if displayType == 'tree':
         return self.DisplayDevicesAsTree(vm, attrsList, useVt100Chars)
      elif displayType == 'list':
         return self.DisplayDevicesAsTable(vm)
      else:
         raise ValueError('Illegal displayType: "%s"' % displayType)

   def DisplayDevicesAsTable(self, vm):
      """
      Display virtual devices as a table.
      """

      return vm.GetAllDevices()

   def DisplayDevicesAsTree(self, vm, attrs, useVt100Chars):
      """
      Display virtual devices as a tree.
      """

      def FormatRecord(record):
         return ', '.join(
            [str(rec_getattr(record, attr)) for attr in attrs]
            ).rstrip()

      def GetDevices(obj):
         if isinstance(obj, Tree.Node):
            return [device for device in vm.GetAllDevices()
                    if device.controller is None]
         elif hasattr(obj, 'managedObject'):
            if hasattr(obj.managedObject, 'device'):
               return [vm.GetDevice(key) for key in obj.managedObject.device]
            else:
               return []


      rootNode = Tree.Node(nodeLabel=vm.name)

      print Tree.FormatAsTree(data=rootNode,
                              labelAttr='nodeLabel',
                              labelFunc=FormatRecord,
                              childrenFunc=GetDevices,
                              useVt100LineDrawingChars=useVt100Chars)


class ConnectDevice(Operation):

   usage = '<device_name>'

   def DoIt(self, host, vm, deviceName):
      """
      Connect a virtual device.

      Example scenario:

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig floppy0.connectable.connected
      getconfig(floppy0.connectable.connected) = 0

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' connectdevice floppy0
      connectdevice(floppy0) = success

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig floppy0.connectable.connected
      getconfig(floppy0.connectable.connected) = 1
      """

      vm = Operation.GetVm(host, vm)

      device = vm.GetDevice(deviceName)
      device.SetConnected(True)

      return device.Save()


class DisconnectDevice(Operation):

   usage = '<device_name>'

   def DoIt(self, host, vm, deviceName):
      """
      Disconnect a virtual device.

      Example scenario:

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig floppy0.connectable.connected
      getconfig(floppy0.connectable.connected) = 1

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' disconnectdevice floppy0
      disconnectdevice(floppy0) = success

      $ ./vmware-cmd2 -H pioneer-131 'VirtualCenter 2.5 VM' getconfig floppy0.connectable.connected
      getconfig(floppy0.connectable.connected) = 0
      """

      vm = Operation.GetVm(host, vm)

      device = vm.GetDevice(deviceName)
      device.SetConnected(False)

      return device.Save()
