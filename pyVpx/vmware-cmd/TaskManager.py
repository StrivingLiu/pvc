import sys, Utils
from Task import Task, TaskBlocked


class TaskManager(object):

   def __init__(self):
      self.tasks = []
      self.verbose = False

   def HandleIfTask(self, arg, async=False):
      if not Utils.IsPyVmomiTask(arg): return arg
         
      task = Task(arg)

      if async:  return self.QueueTask(task)
      else:      return self.WaitForTask(task)
            
   def QueueTask(self, task):         
      self.tasks.append(task)
      return str(task)

   def WaitForTask(self, task):
      while 1:
         try:
            self.OnTaskWait(task)
            task.OnProgressUpdate = self.OnTaskProgressUpdate
            result = task.WaitForCompletion()
            task.OnProgressUpdate(task, percentDone=100)
            self.OnTaskDone(task, task.info.state, result)
            return result
         except TaskBlocked:
            task.OnProgressUpdate(task, percentDone=95)
            self.OnTaskBlocked(task)

   def CheckPendingTasks(self):
      for task in self.tasks:
         task.CheckForUpdates()
         
         if task.IsBlockedOnQuestion():
            self.OnTaskBlocked(task)

         if not task.IsRunning():
            self.OnTaskDone(task, task.info.state, task.info.result)
            task.filter.Destroy()
            self.tasks.remove(task)

   def OnTaskWait(self, task):
      if self.verbose:
         sys.stderr.write('# Waiting for task %s to complete ...\n' % task)

   def OnTaskProgressUpdate(self, task, percentDone):
      pass

   def OnTaskDone(self, task, state, result):
      if self.verbose:
         sys.stderr.write('# Task %s: %s with result = %s.\n' % (task, state, result))

   def OnTaskBlocked(self, task):
      raise


      
