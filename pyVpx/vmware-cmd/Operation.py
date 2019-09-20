import inspect
from Vm import Vm


class Operation(object):
   """
   A base class for operations

   To define new operations, you should subclass Operation and then
   define an appropriate DoIt method - i.e.:

   def DoIt(self, host): pass
   def DoIt(self, host, vm): pass
   """

   usage = ''
   notes = ''

   @staticmethod
   def GetVm(host, arg):
      if not isinstance(arg, Vm): arg = host.GetVm(arg)
      return arg

   @staticmethod
   def GetVmEx(host, arg):
      if not isinstance(arg, Vm):
          arg = host.GetVmEx(arg)
      return arg

   @classmethod
   def GetName(cls):
      return cls.__name__.lower()

   @classmethod
   def GetArgSpec(operation):
      allArgsStr = inspect.formatargspec(
         *inspect.getargspec(operation.DoIt))[1:-1]
      allArgsList = allArgsStr.split(', ')

      return ' '.join(['<%s>' % arg for arg in allArgsList
                       if arg not in ['self', 'host', 'vm']])

   def __init__(self):
      self.name = self.__class__.GetName()
