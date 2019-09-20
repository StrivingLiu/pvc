import pyVmomi, pyVim.connect, pyVim.task

TaskBlocked = pyVim.task.TaskBlocked


class Task(object):

   def __init__(self, managedObject):
      self.managedObject = managedObject
      self.serviceInstance = pyVim.connect.GetSi()
      self.propertyCollector = self.serviceInstance.content.propertyCollector
      self.filter = pyVim.task.CreateFilter(self.propertyCollector, 
                                            self.managedObject)
      self.version = None
      
   def WaitForCompletion(self):
      return pyVim.task.WaitForTask(task=self.managedObject,
                                    si=self.serviceInstance,
                                    pc=self.propertyCollector,
                                    onProgressUpdate=self.OnProgressUpdate)

   def CheckForUpdates(self):
      update = self.propertyCollector.CheckForUpdates(self.version)
      self.version = update.version

   def IsRunning(self):
      return (self.managedObject.info.state == 'running')

   def IsBlockedOnQuestion(self):
      vm = self.managedObject.info.entity
      if vm is not None:
         return vm.runtime.question

   def OnProgressUpdate(self, task, percentDone): pass   

   def __str__(self):
      return 'Task(%s, %s)' % (self.info.descriptionId, self.info.entityName)

   def __getattr__(self, name):
      """ Delegate unknown attributes/methods to the managedObject """

      return getattr(self.managedObject, name)

