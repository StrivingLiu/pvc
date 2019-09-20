from signal import signal, alarm, SIGALRM
from time import sleep


class Task(object):

   def __init__(self, taskName, func, sleepSeconds, returnValue):
      self.taskName = taskName
      self.func = func
      self.sleepSeconds = sleepSeconds
      self.returnValue = returnValue
      self.done = False
      self.Execute()

   def Execute(self):
      def _sigalrmHandler(signum, frame):
         self.func()
         self.done = True

      signal(SIGALRM, _sigalrmHandler)
      alarm(self.sleepSeconds)

   def __str__(self):
      return "'%s.%s:%s'" % (self.__module__,
                             self.__class__.__name__,
                             self.taskName)

   def WaitForCompletion(self):
      while not self.done: sleep(0.2)

      return self.returnValue
