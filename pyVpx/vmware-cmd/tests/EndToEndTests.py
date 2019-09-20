#!/usr/bin/env python

"""
"""

import atexit, os, re, string, subprocess, sys, testoob, unittest
import pyVim.vm, pyVim.invt, pyVim.task, pyVmomi
sys.path.append('..')
from Host import Host
from TableDrivenTestCase import TableDrivenTestCase


hostName  = os.getenv('VIM_E2E_HOST')

try:
   logname = os.getlogin()
except Exception:
   logname = os.getenv('LOGNAME')

vm        = 'vmware-cmd_e2eTest_%s' % (logname)
host      = None


class EndToEndTests(TableDrivenTestCase):

   testTableInputFile = file('EndToEndTestsTable.txt')

   @classmethod
   def createTest(cls, argsStr, expRc, expOut,
                  expErr='???'):
      expRc = int(expRc)

      argsStr2 = string.Template(argsStr).safe_substitute(**globals())
      argv = argsStr2.split()

      def ok(result, idx=1):
         return '%s\(%s\) = %s' % (argv[idx], ', '.join(argv[idx+1:]), result)

      expOut2 = eval(string.Template(expOut).safe_substitute(**globals()))

      def testMethod(self):
         (exitStatus, outText, errText) = self.exec_tool(argsStr2)
         #print('exitStatus = "%s"' % exitStatus)
         #print('outText = "%s"' % outText)

         self.assertEqual(exitStatus, expRc)

         if outText.endswith('\n'): outText = outText[:-1]
         if len(outText.splitlines()) > 1:
            shortOutText = outText.splitlines()[0] + '...'
         else:
            shortOutText = outText
         self.failIf(not re.search(expOut2, outText),
                     'output "%s" did not match regex: "%s"; stderr had "%s"'
                     % (outText, expOut2, errText))

         if len(errText) > 0:
            if errText.endswith('\n'): errText = errText[:-1]
            if len(errText.splitlines()) > 1:
               shortErrText = errText.splitlines()[0] + '...'
            else:
               shortErrText = errText
            self.failIf(not re.search(expErr, errText),
                        'stderr "%s" did not match regex: "%s"'
                        % (shortErrText, expErr))

      testDesc = '(`vmware-cmd %s` =~ "%s")' % (argsStr, expOut2 or expErr)
      return testDesc, testMethod

   def setUp(self):
      global host, vm

      if host is None:
         #print('Connecting to %s...' % hostName)
         host = Host(hostName, os.getenv('VIM_E2E_USER'), os.getenv('VIM_E2E_PASSWORD'))
         host.Connect()
         #print('Creating vm %s...' % vm)
         CreateVm(vm)

         def onExit():
            global host, vm

            #print('Deleting vm %s...' % vm)
            DeleteVm(host, vm)
            host.Logout()

         atexit.register(onExit)

   def exec_tool(self, argsStr):
      cmd = 'python ../Main.py -H %s %s' % (hostName, argsStr)
      p = subprocess.Popen(cmd.split(),
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
      outText, errText = p.communicate()
      exitStatus = p.returncode
      return (exitStatus, outText, errText)


EndToEndTests.createTests()


def CreateVm(vmName):
   configSpec = GetConfigSpec(vmname=vmName)
   task = pyVim.invt.GetVmFolder().CreateVm(configSpec,
                                            pyVim.invt.GetResourcePool())
   return pyVim.task.WaitForTask(task)

def PowerOffVm(host, vmName):
   task = host.GetVm(vmName).managedObject.PowerOff()
   return pyVim.task.WaitForTask(task)

def DeleteVm(host, vmName):
   try:
      PowerOffVm(host, vmName)
   except pyVmomi.vim.fault.InvalidPowerState:
      pass

   task = host.GetVm(vmName).managedObject.Destroy()
   return pyVim.task.WaitForTask(task)

def GetConfigSpec(vmname='vmware-cmd_e2eTest',
                  annotation='vmware-cmd test',
                  memory=256,
                  guest='dosGuest',
                  diskSizeInMB=1,
                  numCPUs=1):
   configSpec = pyVim.vm.CreateQuickDummySpec(vmname=vmname,
                                              numScsiDisks=1,
                                              numIdeDisks=0,
                                              memory=memory,
                                              diskSizeInMB=diskSizeInMB)
   configSpec.numCPUs = numCPUs
   configSpec.annotation = annotation

   return configSpec


# Start program
if __name__ == "__main__":
   testoob.main()
