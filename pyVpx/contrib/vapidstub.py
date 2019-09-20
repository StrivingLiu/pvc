#
# vapidstub.py: Stubs for standing up standalone vAPId web services using Python.
#

import datetime
import pyVmomi
from pyVmomi import VmomiSupport
import uuid
import sys
if sys.version_info[0] >= 3:
   from http.cookies import SimpleCookie
else:
   from Cookie import SimpleCookie

# Implementation of the vim.SessionManager managed object interface.  Needed so that
# the esxcli can login to the system.
#
# This implementation just accepts any Login attempt.
class SessionManager(pyVmomi.vim.SessionManager):
   ## Constructor
   #
   def __init__(self, moId='SessionManager'):
      pyVmomi.vim.SessionManager.__init__(self, moId)

   @property
   def currentSession(self):
      session = pyVmomi.vim.UserSession(key='523a3504-e291-1b48-5bc2-37f29cab38e2',
                                        userName="root",
                                        fullName="Root user",
                                        loginTime=datetime.datetime.now(),
                                        lastActiveTime=datetime.datetime.now(),
                                        locale = 'en',
                                        messageLocale = 'en')
      return session

   def Login(self, userName, password, locale=None):
      #Set the Http SessionCookie for the mob to work correctly.
      sessionCookie = str(uuid.uuid1())
      httpContext = VmomiSupport.GetHttpContext()
      if "cookies" in httpContext:
         httpContext["cookies"]["vmware_soap_session"] = sessionCookie
      else:
         cookie = SimpleCookie()
         cookie["vmware_soap_session"] = sessionCookie
         httpContext["cookies"] = cookie
      return self.currentSession

   def Logout(self):
      return

# Implementation of just enough of the vim.ServiceInstance managed object interface to
# get the SessionManager so that esxcli can login to the system.
class ServiceInstance(pyVmomi.vim.ServiceInstance):
   def __init__(self, moId='ServiceInstance', sessionManager=None):
      pyVmomi.vim.ServiceInstance.__init__(self, moId)
      self._sessionManager = sessionManager

   def RetrieveContent(self):
      return pyVmomi.vim.ServiceInstanceContent(
         rootFolder=pyVmomi.vim.Folder("RootFolder", None),
         propertyCollector=pyVmomi.vmodl.query.PropertyCollector("PropertyCollector", None),
         about=pyVmomi.vim.AboutInfo(name="",
                                     fullName="",
                                     vendor="",
                                     version="",
                                     build="",
                                     osType="",
                                     productLineId="",
                                     apiType="",
                                     apiVersion=""),
         sessionManager=self._sessionManager)

# Rrename the hard-coded python DynamicTypeManager to be THE hard-coded
# C++ DynamicTypeManager that esxcli depends upon.  Use the fact that the
# moId internal to the object is not the identifier that is used to locate
# the managed object.
def CreateProxyDynamicTypeManager():
   import MoManager
   moManager = MoManager.GetMoManager()
   dynamicTypeManager = moManager.LookupObject("ha-dynamic-type-manager-python")
   moManager.RegisterObject(dynamicTypeManager, "ha-dynamic-type-manager")

# Create and register managed objects
def RegisterVIAPIManagedObjectStubs(vorb, registerProxyDTM=True):
   sessionManager = SessionManager("SessionManager")
   vorb.RegisterObject(sessionManager)

   serviceInstance = ServiceInstance("ServiceInstance", sessionManager)
   vorb.RegisterObject(serviceInstance)

   if registerProxyDTM:
      CreateProxyDynamicTypeManager()
