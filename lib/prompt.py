import sys
import copy

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import prompt, CompleteStyle
from prompt_toolkit.key_binding import KeyBindings
from history import GenerateHistory


PY3K = sys.version_info >= (3, 0)

def UnicodeConvert(obj=None):
   if isinstance(obj,str):
      return obj.decode()
   elif isinstance(obj, list):
      return [UnicodeConvert(item) for item in obj]
   elif isinstance(obj, dict):
      ret = {}
      for key,value in obj.items():
         ret[UnicodeConvert(key)] = UnicodeConvert(value)
      return ret
   else:
      return None



BASIC_COMMAND = {
   'ls' : {'args' : None,
         'desc' : 'Change directory'},
   'cd': {'args': None,
         'desc': 'Change directory'}
}

BASIC_DESC = 'Press `Tab` : show command, `Up-Down-Left-Right` : Move,'\
           " `Space` : Select, Type 'exit' : exit"


class Completer(Completer):
   """
   This is a completer that's very slow.
   """
   def __init__(self, cmd = None):
      self.loading = 0
      self.init_cmds = cmd
      self.runtime_cmds = copy.copy(list(cmd))

   def UpdateCmd(self, cmds = None):
      if cmds is not None:
         for cmd in cmds:
            if cmd not in self.init_cmds:
               self.init_cmds.append(cmd)

   def ChangeCompletion(self, loadcmds = None):
      self.runtime_cmds = copy.copy(list(self.init_cmds))\
         if loadcmds is None else copy.copy(list(loadcmds))

   def get_completions(self, document, complete_event):
      # Keep count of how many completion generators are running.
      self.loading += 1
      word_before_cursor = document.get_word_before_cursor()

      try:
         for word in self.runtime_cmds:
            if word.startswith(word_before_cursor):
               yield Completion(word, -len(word_before_cursor))

      finally:
         # We use try/finally because this generator can be closed if the
         # input text changes before all completions are generated.
         self.loading -= 1

class Prompt():

   def __init__(self, persistent_history = True):
      self.bindings = KeyBindings()
      self.cmds = {}
      self.completer = Completer(self.cmds.keys())
      self.toolbar = BASIC_DESC
      self.history = GenerateHistory('./pvc', persistent_history)
      self.path = '/'

      @self.bindings.add(' ')
      def _(event):
         """
         When space is pressed, we check the word before the cursor, and
         autocorrect completion.
         """
         buffer = event.app.current_buffer
         cmdstr = buffer.document.get_word_before_cursor()
         buffer.insert_text(' ')
         if cmdstr and not cmdstr.isspace():
            cmdname = cmdstr.split()[0]
            if cmdname in self.cmds.keys():
               showArgs = self.cmds[cmdname]['args']
               showArgs = showArgs if showArgs is not None else [' ']
               self.completer.ChangeCompletion(loadcmds = showArgs)
               self.toolbar = self.cmds[cmdname].get('desc', 'No Description')

   def change_path(self, path):
      self.path = path

   def add_cmds(self, cmdList=None):
      if cmdList is not None:
         if not PY3K:
            cmdList = UnicodeConvert(cmdList)
         self.cmds.update(cmdList)
         self.completer.UpdateCmd(cmdList.keys())

   def _restate(self):
      self.toolbar = BASIC_DESC
      self.completer.ChangeCompletion()

   def _getBottomToolbar(self):
      return self.toolbar

   def _wrap_path(self):
      return '%s %s> ' % ('pvc-1.0', self.path)

   def get(self):
      while True:
         self._restate()
         cmd = prompt(self._wrap_path(), completer=self.completer,
            key_bindings=self.bindings, complete_in_thread=True,
            complete_while_typing=True, refresh_interval=.5,
            bottom_toolbar=self._getBottomToolbar,
            complete_style=CompleteStyle.MULTI_COLUMN,
            history=self.history)
         if cmd and not cmd.isspace():
                return cmd

_gPrompt = None
def GetPrompt():
   global _gPrompt
   if not _gPrompt:
      _gPrompt = Prompt()
   return _gPrompt
