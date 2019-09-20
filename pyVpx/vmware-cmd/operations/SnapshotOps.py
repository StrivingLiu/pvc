from Operation import Operation
from CommandProcessor import InvalidParameter
import Tree


class HasSnapshot(Operation):

   usage = ''

   def DoIt(self, host, vm):
      """
      Example:

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 hassnapshot
      hassnapshot() = 0

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 createsnapshot test_snapshot 'a test snapshot' 1 1
      createsnapshot(test_snapshot, a test snapshot, 1, 1) = success

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 hassnapshot
      hassnapshot() = 1
      """

      vm = Operation.GetVm(host, vm)

      if vm.snapshot: return 1
      else: return 0


class ShowSnapshotTree(Operation):

   hidden = True
   
   def DoIt(self, host, vm, useVt100LineDrawingChars=False):
      """
      Examples:

      $ ./vmware-cmd -H pivot02 mabramow-test1 showsnapshottree
      mabramow-test1
      `- foo
         |- Marc
         |  |- Nicole
         |  `- Test 1
         `- Test 2
            `- Test 3
      """

      vm = Operation.GetVm(host, vm)

      rootNode = Tree.Node(name=vm.name,
                           childSnapshotList=vm.snapshot.rootSnapshotList)

      print Tree.FormatAsTree(data=rootNode,
                              labelAttr='name',
                              childrenAttr='childSnapshotList',
                              useVt100LineDrawingChars=useVt100LineDrawingChars)


class CreateSnapshot(Operation):

   usage = '<name> <description> <quiesce> <memory>'

   def GetParamValue(self, stringParam, paramName):
      """
      Convert expected (0 or 1) input string value into
      a proper boolean value.
      """
      try:
         return bool(int(stringParam))
      except ValueError, e:
         raise InvalidParameter("Invalid value for %s parameter, should be 0 or 1" % paramName)


   def DoIt(self, host, vm, name, description, quiesce, memory):
      """
      Example:

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 hassnapshot
      hassnapshot() = 0

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 createsnapshot test_snapshot 'a test snapshot' 1 1
      createsnapshot(test_snapshot, a test snapshot, 1, 1) = success

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 hassnapshot
      hassnapshot() = 1
      """

      """
      print('### CreateSnapshot.DoIt: ' +
            'vm = %s; ' % vm +
            'name = "%s"; ' % name +
            'description = "%s"; ' % description +
            'quiesce = %s; ' % bool(int(quiesce)) +
            'memory = %s; ' % bool(int(memory)))
      """

      vm = Operation.GetVm(host, vm)

      memory = self.GetParamValue(memory, 'memory')
      quiesce = self.GetParamValue(quiesce, 'quiesce')
      return vm.CreateSnapshot(name, description, memory, quiesce)


class RevertSnapshot(Operation):

   usage = ''

   def DoIt(self, host, vm):
      vm = Operation.GetVm(host, vm)

      return vm.RevertToCurrentSnapshot()


class RemoveSnapshots(Operation):

   usage = ''

   def DoIt(self, host, vm):
      """
      Example:

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 hassnapshot
      hassnapshot() = 1

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 removesnapshots
      removesnapshots() = success

      $ ./vmware-cmd2 -H pivot02 mabramow-test1 hassnapshot
      hassnapshot() = 0
      """

      vm = Operation.GetVm(host, vm)

      return vm.RemoveAllSnapshots()
