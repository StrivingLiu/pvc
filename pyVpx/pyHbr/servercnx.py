#
# pyHbr.serverCnx.py
#
# Python wrappers for SOAP connections.
#
# Not meant to be invoked directly.  Shared utility code for other hbrsrv
# wrappers.
#
import httplib
import logging
import pyHbr.exceptions
import pyVim.connect
import ssl

from pyVim.connect import VimSessionOrientedStub, SmartStubAdapter
from pyVmomi import Hbr
from pyVmomi import Hostd
from pyVmomi import Vim
from pyVmomi import Vmodl, SoapStubAdapter, SessionOrientedStub
from pyVmomi.VmomiSupport import newestVersions

logger = logging.getLogger('pyHbr.servercnx')

DEFAULT_VMODL_PORT = 8123

#
# This corresponds to the HBR VMODL API version that will be used to connect
# to the hbrsrv.
#
HBR_CURRENT_VMODL_VERSION = newestVersions.get('hbr.replica')

#
# This is the list of vim versions that we'll connect to in order
# of most to least preference. The current version should always
# be first so we can use it if it's available.
#
# When new vim versions are added we need to add them here.
#
# See $VMTREE/vim/vmodl/vim/version/version<latest num>.java
#
HBR_VIM_VERSIONS = [
        newestVersions.get('vim'),
        "vim.version.version12",
        "vim.version.version11",
        "vim.version.version10",
        "vim.version.version9",
]

class HbrsrvSessionOrientedStub(SessionOrientedStub):
   """A hbrsrv-specific SessionOrientedStub.  See the SessionOrientedStub class
   in pyVmomi/SoapAdapter.py for more information."""

   # The set of exceptions that should trigger a relogin by the session stub.
   SESSION_EXCEPTIONS = (
      Vmodl.fault.SecurityError
   )

   @staticmethod
   def MakeUserPasswordLoginMethod(username, password):
      """Create a closure that will call the SessionManager.Login()
      method with the given parameters."""
      def _doLogin(soapStub):
         smgr = HbrSessionManager(soapStub)
         smgr.Login(username, password)

         logger.debug('Connected to the hbrsrv with user/password')
      return _doLogin

   @staticmethod
   def MakeThumbprintLoginMethod():
      """Create a closure that will call the SessionManager.LoginBySSLThumbprint()
      method with the given parameters."""
      def _doLogin(soapStub):
         smgr = HbrSessionManager(soapStub)
         try:
            smgr.LoginBySSLThumbprint()
         except Hbr.Replica.Fault.InvalidLogin:
            #
            # If a new certificate was just pushed to the hbrsrv, we may need to
            # ReadGuestInfoKeys before we can login with our ssl certificate
            #
            smgr.ReadGuestInfoKeys()
            smgr.LoginBySSLThumbprint()

         logger.debug('Connected to the hbrsrv using the thumbprint')
      return _doLogin


def CreateHbrsrvSoapStub(host,
                         port=DEFAULT_VMODL_PORT,
                         version=HBR_CURRENT_VMODL_VERSION,
                         username=None,
                         password=None,
                         keyFile=None,
                         certFile=None,
                         reliableCnx=False):
   soapStub = SoapStubAdapter(host=host,
                              port=port,
                              version=version,
                              path='/',
                              certFile=certFile,
                              certKeyFile=keyFile,
                              sslContext=ssl._create_unverified_context())

   if not reliableCnx:
      return soapStub

   if keyFile is not None and certFile is not None:
      loginMethod = HbrsrvSessionOrientedStub.MakeThumbprintLoginMethod()
      logger.debug('Creating a new SOAP stub using thumbprint authentication')
   elif username is not None and password is not None:
      loginMethod = HbrsrvSessionOrientedStub.MakeUserPasswordLoginMethod(username,
                                                                          password)
      logger.debug('Creating a new SOAP stub using user/password authentication')
   else:
      raise pyHbr.exceptions.ConnectionError('Missing credentials.')

   soapStub = HbrsrvSessionOrientedStub(soapStub,
                                        loginMethod,
                                        retryDelay=0.1,
                                        retryCount=4)
   return soapStub

def CreateHostdSoapStub(host,
                        username,
                        password):
   stub = pyVim.connect.SmartStubAdapter(host=host,
                                         preferredApiVersions=HBR_VIM_VERSIONS,
                                         sslContext=ssl._create_unverified_context())

   # Create a hostd connection using the more robust SessionOrientedStub
   loginMethod = VimSessionOrientedStub.makeUserLoginMethod(username, password)

   return VimSessionOrientedStub(stub,
                                 loginMethod,
                                 retryDelay=0.5,
                                 retryCount=20)

def ServiceInstance(soapCnx):
   return Vim.ServiceInstance("ServiceInstance", soapCnx)

def HostdHbrInternalSystem(soapCnx):
   return Hostd.HbrInternalSystem('ha-hbr-internal-manager', soapCnx)

def HbrReplicationManager(soapCnx):
   # The global ReplicationManager has a fixed MOID of 'HbrServer' so just
   # fabricate a stub for that VMODL object.  Everything else is reachable
   # off this.
   return Hbr.Replica.ReplicationManager("HbrServer", soapCnx)

def HbrSessionManager(soapCnx):
   # The global ReplicationManager has a fixed MOID of 'HbrServer' so just
   # fabricate a stub for that VMODL object.  Everything else is reachable
   # off this.
   return Hbr.Replica.SessionManager("HbrSessionManager", soapCnx)

def HbrServerManager(soapCnx):
   # The global ReplicationManager has a fixed MOID of 'HbrServer' so just
   # fabricate a stub for that VMODL object.  Everything else is reachable
   # off this.
   return Hbr.Replica.ServerManager("HbrServerManager", soapCnx)
