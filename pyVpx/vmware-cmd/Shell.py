import atexit, cmd, inspect, os, readline, shlex, sys
from cmd import Cmd
import CommandProcessor, operations, optionsParser, Host
from Formatter import Formatter, FormatOptions
from TaskManager import TaskManager
from TerminalController import ProgressBar


class Shell(Cmd):

   def __init__(self, host):
      Cmd.__init__(self)

      self.host = host
      self.formatter = Formatter.GetByType('simple')
      self.progressBar = None

      self.SetupTaskManager()
      self.SetPrompt()
      self.SetupFormatters()
      self.SetupReadline()
      self.ReadRcFile()

      for opName, op in operations.opsDict.items():
         setattr(self, 'do_%s' % opName, self.GetFunc(opName, op))
         setattr(self, 'help_%s' % opName, self.GetHelpFunc(opName, op))

   def SetupTaskManager(self):      
      taskManager = TaskManager()
      taskManager.OnTaskBlocked = self.OnTaskBlocked
      taskManager.OnTaskWait = self.OnTaskWait
      taskManager.OnTaskProgressUpdate = self.OnTaskProgressUpdate
      taskManager.OnTaskDone = self.OnTaskDone
      self.taskManager = taskManager
      
   def SetupFormatters(self):
      FormatOptions.GetByName('Vm').SetColumns(
         ['moId',
          'name',
          'powerState',
          'questionPending'
          ])

   def SetupReadline(self):
      readline.set_completer_delims(' ')
      historyFile = os.path.expanduser('~/.vmware-cmd_history')
      atexit.register(readline.write_history_file, historyFile)
      if os.path.exists(historyFile):
         readline.read_history_file(historyFile)

   def ReadRcFile(self):
      rcFile = os.path.expanduser('~/.vmware-cmd_shell_rc')
      if os.path.exists(rcFile): execfile(rcFile)

   def OnTaskWait(self, task):
      header = '%s (%s)' % (task.info.descriptionId, task.info.entityName)

      try:
         self.progressBar = ProgressBar(header)
      except Exception, e:
         self.progressBar = None
         print('Waiting for %s to complete ...' % task)

   def OnTaskBlocked(self, task):
      if self.progressBar: self.progressBar.clear()

      print('\nVirtual machine requires user input to continue')

      operations.Answer().DoIt(host=self.host, vm=task.info.entity)

   def OnTaskProgressUpdate(self, task, percentDone):
      if percentDone is None: return

      if self.progressBar:
         self.progressBar.update(percentDone, message='')
      else:
         print('%s: %d%% complete ...' % (task, percentDone))

   def OnTaskDone(self, task, state, result):
      if self.progressBar: self.progressBar.clear()
         
      print('%s: %s' % (task, state))

   def emptyline(self):      
      return self.taskManager.CheckPendingTasks()

   def get_names(self):
      return [ x for x in dir(self)
               if x.startswith('do_') or x.startswith('help_') ]

   def completedefault(self, text, line, begidx, endidx):
      text = text.replace("\\", "")
      
      return [ vm.name.replace(" ", "\ ").replace("'", "\\'")
               for vm in self.host.GetVms()
               if vm.name.startswith(text) ]

   def do_connect(self, argsString):
      args = shlex.split(argsString)
      host = Host.Host(*args)
      self.host = host
      self.SetPrompt()

   def do_shell(self, arg):
      os.system(arg)

   def do_echo(self, arg):
      print(str(arg))

   def default(self, line):
      try:
         print(eval(line))
      except:
         try:
            exec(line) in globals()
         except Exception, e:
            print('%s' % e)

   def do_quit(self, arg):
      return True

   def do_exit(self, arg):
      return True

   def do_EOF(self, arg):
      print('')
      return True

   def GetFunc(self, operationName, operation):
      def innerFunc(argsString):
         try:
            if argsString.endswith('&'):
               async = True
               argsString = argsString[:-1]
            else:
               async = False
            
            _operationName, result = CommandProcessor.Process(
               self.host,
               args=[operationName] + shlex.split(argsString))

            result = self.taskManager.HandleIfTask(result, async)
               
            print(self.formatter.Format(result))
         except KeyboardInterrupt:
            print >>sys.stderr, '\nKeyboardInterrupt'
         except Exception, e:
            print >>sys.stderr, 'Exception: %s' % e

      return innerFunc

   def GetHelpFunc(self, operationName, operation):
      def innerFunc():
         print('\n   %s %s\n   %s\n%s'
               % (operationName, operation.usage,
                  self.GetArgSpec(operation), operation.__doc__ or ''))

      return innerFunc

   @staticmethod
   def GetArgSpec(operation):
      allArgsStr = inspect.formatargspec(
         *inspect.getargspec(operation.DoIt))[1:-1]
      allArgsList = allArgsStr.split(', ')

      return ' '.join(['<%s>' % arg for arg in allArgsList
                       if arg not in ['self', 'host', 'vm']])

   def SetPrompt(self):
      if not sys.stdin.isatty():
         self.prompt = ''
         return

      if self.host:  hostname = self.host.hostname
      else:          hostname = 'no_host'

#       self.prompt = '%(blueOn)svmware-cmd://%(hostname)s >>%(colorOff)s ' % \
#          dict(hostname=hostname,
#              blueOn='\033[01;34m',
#              colorOff='\033[00m')

      self.prompt = 'vmware-cmd://%s >> ' % hostname
