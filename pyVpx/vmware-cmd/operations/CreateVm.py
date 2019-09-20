import os, shutil, sys, pprint, tempfile

try:
   import yaml
except ImportError:
   pass
   #sys.stderr.write('CreateVm.py: Could not import yaml Python module')

import pyVim.vm
import pyVim.invt
from Operation import Operation
from TerminalController import TerminalController


class CreateVm(Operation):
   """
   Create a new virtual machine.
   """

   hidden = True
   
   def DoIt(self, host):
      """
      Example:

      $ ./vmware-cmd2 -H sdk167 createvm
      ???
      """

      if 'yaml' not in globals():
         raise ImportError('CreateVm.py requires yaml Python module')

      configSpec = self.GetConfigSpec()

      if self.CreateVmConfirmed(configSpec):
         return self.CreateVm(configSpec)
      else:
         print('Create vm operation aborted.')

   def GetConfigSpec(self):
      tmpFile = self.InvokeEditorOnFile(self.CreateTemplateFile())
      yamlObj = yaml.load(tmpFile)

      configSpec = pyVim.vm.CreateQuickDummySpec(vmname=yamlObj['Name'],
                                                 numScsiDisks=1,
                                                 numIdeDisks=0,
                                                 memory=yamlObj['Memory'],
                                                 diskSizeInMB=yamlObj['Hard Disk']['Size']
                                                 )
      configSpec.numCPUs = yamlObj['Num CPUs']
      configSpec.annotation = yamlObj['Annotation']

      return configSpec

   def CreateTemplateFile(self):
      tmpFile = tempfile.NamedTemporaryFile()
      shutil.copy('%s/CreateVmTemplate.yaml' % os.path.dirname(sys.argv[0]), tmpFile.name)
      return tmpFile

   def InvokeEditorOnFile(self, aFile):
      editor = os.getenv('EDITOR') or 'vi'
      os.system('%s %s' % (editor, aFile.name))
      sys.stdout.write(TerminalController().NORMAL)
      return aFile

   def CreateVmConfirmed(self, configSpec):
      pprint.pprint(configSpec)
      ch = raw_input('\nCreate vm with above configSpec? [n] ')
      return (ch == 'y')

   def CreateVm(self, configSpec):
      return pyVim.invt.GetVmFolder().CreateVm(configSpec,
                                               pyVim.invt.GetResourcePool())
