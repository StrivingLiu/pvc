from Operation import Operation


class ListTasks(Operation):
   """
   List recent tasks.
   """

   hidden = True
   usage = ''

   def DoIt(self, host):
      """
      Example:

      $ ./vmware-cmd2 -H pivot02 listtasks
      SessionManager.login       None              success    None                                                                               2008-06-11T00:27:07.82291Z
      VirtualMachine.reset       mabramow-test1    error      The attempted operation cannot be performed in the current state (Powered Off).    2008-06-11T00:36:06.776436Z
      VirtualMachine.answer      mabramow-test1    success    None                                                                               2008-06-11T00:36:43.335496Z
      VirtualMachine.powerOn     mabramow-test1    success    None                                                                               2008-06-11T00:36:44.606386Z
      VirtualMachine.powerOff    mabramow-test1    success    None                                                                               2008-06-11T00:36:53.195174Z
      """

      return host.serviceInstance.content.taskManager.recentTask
