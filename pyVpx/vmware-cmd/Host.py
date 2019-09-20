import atexit, getpass, sys
import pyVmomi
import pyVim.connect
import pyVim.folder
from pyVim.host import GetHostSystem

from PathConverter import PathConverter
from Vm import Vm


class NotConnected(pyVmomi.vim.Fault.HostConnectFault): pass


class NullHost(object):

   def __init__(self, hostname='localhost'):
      self.hostname = hostname

   def Connect(self): pass

   def __str__(self):
      return object.__str__(self)

   def __repr__(self):
      return object.__str__(self)

   def __getattr__(self, name):
      raise NotConnected()


def LogoutConnectedHosts():
   for host in Host.connectedHosts:
      host.Logout()

atexit.register(LogoutConnectedHosts)


class Host(object):

   connectedHosts = []

   @classmethod
   def GetHost(cls, tup):
      return cls(*tup)

   def __init__(self, hostname, user, password, namespace='vim25/5.5'):
      self.hostname = hostname
      self.user = user
      self.password = password
      self.namespace = namespace
      self._vmList = []
      self._nameToVm = {}
      self._serviceInstance = None

   def Connect(self):
      if self.hostname == 'localhost' and not self.password:
         self.user, self.password = self.GetUserNameAndPasswordWithLocalTicket()

      if self.password is None:
         self.password = getpass.getpass('Password: ')

      try:
         self._serviceInstance = pyVim.connect.Connect(
            host=self.hostname,
            user=self.user,
            pwd=self.password,
            namespace=self.namespace)
         self.__class__.connectedHosts.append(self)
         pyVim.connect.SetSi(self._serviceInstance)
         self.configManager = self.hostSystem.configManager
         self.datastoreSystem = self.configManager.datastoreSystem
         self.pathConverter = PathConverter(self.hostSystem.datastore)
         self.GetLocalPathFromDsPath = self.pathConverter.GetLocalPathFromDsPath
         self.GetDsPathFromLocalPath = self.pathConverter.GetDsPathFromLocalPath
         return self._serviceInstance
      except Exception, e:
         raise pyVmomi.Vim.Fault.HostConnectFault()

   def GetUserNameAndPasswordWithLocalTicket(self):
      soapAdapter = pyVmomi.SoapStubAdapter(self.hostname, ns=self.namespace)
      serviceInstance = pyVmomi.Vim.ServiceInstance(
         "ServiceInstance", soapAdapter)
      try:
         sessionManager = serviceInstance.content.sessionManager
      except Exception, e:
         if type(e).__name__ == 'ExpatError':
            raise pyVmomi.Vim.Fault.HostConnectFault(
               msg='Malformed response from hostd while querying for local ticket. (%s)' % e)
         else:
	    if str(e).find("503 ") != -1:  # PR 482756
               descr='Check hostd process, it may be initializing. (%s)' % e
	    else:
               descr='Check hostd process, retrieve local ticket from session manager failed. (%s)' % e
            raise pyVmomi.Vim.Fault.HostConnectFault(msg=descr)
      localTicket = sessionManager.AcquireLocalTicket(userName=getpass.getuser())
      return localTicket.userName, file(localTicket.passwordFilePath).read()

   @property
   def serviceInstance(self):
      """
      Lazily connects when needed
      """

      if not self._serviceInstance:
         self.Connect()

      return self._serviceInstance   

   def Logout(self):
      self.__class__.connectedHosts.remove(self)
      return self.sessionManager.Logout()

   @property
   def about(self):
      return self.serviceInstance.content.about

   @property
   def hostSystem(self):
      return GetHostSystem(self.serviceInstance)

   @property
   def sessionManager(self):
      return self.serviceInstance.content.sessionManager

   @property
   def perfManager(self):
      return self.serviceInstance.content.perfManager

   def GetVms(self):
      self.serviceInstance
      
      if not self._vmList:
         self._vmList = [ Vm(host=self, managedObject=managedObject)
                          for managedObject in pyVim.folder.GetAll() ]

      return self._vmList

   def GetVm(self, arg, default=None):
      self.serviceInstance

      ## `arg` must be a string
      if not hasattr(arg, 'endswith'): return default or arg
      
      try:
         return self.GetVmByCfgPath(arg)
      except pyVmomi.vim.fault.NotFound, msg:
         return self.GetVmByName(arg)

   def GetVmByCfgPath(self, vmxFilename):
      """
      @todo Look at moving path conversion stuff into pyVim or other lib
      """

      self.serviceInstance
      
      dsPath = self.GetDsPathFromLocalPath(vmxFilename)
      managedObject = pyVim.folder.FindCfg(dsPath)
      if managedObject is None:
         raise pyVmomi.vim.fault.NotFound(
            msg='No virtual machine found with config path: %s' \
                % vmxFilename)

      vm = Vm(host=self, managedObject=managedObject)

      if not managedObject: vm.dsPath = dsPath

      return vm

   def GetVmByName(self, name):
      self.serviceInstance
      
      if not self._nameToVm.has_key(name):
         managedObject = pyVim.folder.Find(name)
         if managedObject is None:
            raise pyVmomi.vim.fault.NotFound(
               msg='No virtual machine found with name: ' + name)

         vm = Vm(host=self, managedObject=managedObject)
         self._nameToVm[name] = vm

      return self._nameToVm[name]

   def GetVmBySummaryName(self, name):
      self.serviceInstance

      if (not self._nameToVm.has_key(name)):
         managedObject = pyVim.folder.FindBySummaryName(name)
         if managedObject is None:
            return None

         vm = Vm(host=self, managedObject=managedObject)
         self._nameToVm[name] = vm
         return vm

      return self._nameToVm[name]

   def GetVmBySummaryPath(self, vmxFilename):
      self.serviceInstance

      dsPath = self.GetDsPathFromLocalPath(vmxFilename)
      if (dsPath == None):
         return None

      managedObject = pyVim.folder.FindBySummaryPath(dsPath)
      if managedObject is None:
         return None

      vm = Vm(host=self, managedObject=managedObject)

      if not managedObject:
         vm.dsPath = dsPath

      return vm



   def GetVmEx(self, vmRef):
      """
      Resolve VM name using name and filepath stored in VM Summary
      info.   This allow us to access misconfigured VMs.  At the
      moment of implementation this method is intended to be used
      only to unregister VM.  This method does not throw any
      exception in case VM is not found - it just returns None
      object.

      """

      if (vmRef == None):
         return None

      if (isinstance(vmRef, Vm)):
         return name

      vm = self.GetVmBySummaryPath(vmRef)
      if (vm != None):
         return vm

      return self.GetVmBySummaryName(vmRef)


   def RegisterVm(self, vmxFilename):
      """
      @todo Look at moving path conversion stuff into pyVim or other lib
      """

      self.serviceInstance
      
      dsPath = self.GetDsPathFromLocalPath(vmxFilename)
      return pyVim.folder.Register(dsPath)

   def UnregisterVm(self, vm):
      """
      @todo Look at moving path conversion stuff into pyVim or other lib
      """

      self.serviceInstance
      
      vm.Unregister()

   def GetDatastoreByName(self, datastoreName):
      for datastore in self.hostSystem.datastore:
         if datastoreName == datastore.summary.name: return datastore

   def __getattr__(self, name):
      """ Delegate unknown attributes/methods to the serviceInstance """

      return getattr(self.serviceInstance, name)

   def __repr__(self):
      return '%s(hostname=%s, serviceInstance=%s)' % (type(self).__name__,
                                                      self.hostname,
                                                      self.serviceInstance)
