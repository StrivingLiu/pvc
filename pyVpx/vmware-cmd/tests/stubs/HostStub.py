from Struct import Struct


class VimFault(Exception):
   def __init__(self, message):
      Exception.__init__(self, message)
VimFault.__module__ = 'pyVmomi.vim.fault'

class NotFound(VimFault): pass
NotFound.__module__ = 'pyVmomi.vim.fault'

pyVmomi = Struct(
   vim=Struct(
      fault=Struct(
         NotFound=NotFound,
      )
   )
)


class Host(object):

   def __init__(self, hostname, vmList, **kwargs):
      self.hostname = hostname
      self._nameToVm = {}

      for vm in vmList:
         vm.host = self
         self._nameToVm[vm.name] = vm

      self._vmList = vmList

      # Take keyword arg values passed in and use them to set object attributes
      self.__dict__.update(kwargs)

   def Connect(self):
      pass

   def __eq__(self, other):
      return self.hostname == other.hostname

   def GetVms(self):
      return self._vmList

   def GetVm(self, arg, default=None):
      return self.GetVmByName(arg) or default or arg

   def GetVmByName(self, name):
      if self._nameToVm.has_key(name):
         return self._nameToVm[name]
      else:
         raise pyVmomi.vim.fault.NotFound(
            message='No virtual machine found with name: %s' % name)
