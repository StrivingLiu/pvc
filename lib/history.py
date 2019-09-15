from collections import deque
from prompt_toolkit import PromptSession
from prompt_toolkit.history import History, ThreadedHistory
from prompt_toolkit.history import FileHistory

HISTORY_DEQUE = deque(maxlen=1000)
__all__ = [
   'NonPersistentHistory',
   'PersistentHistory',
]

def GenerateHistory(name, need_persistent = False):
   if need_persistent:
      return PersistentHistory(name)
   else:
      return ThreadedHistory(NonPersistentHistory())

# which is in memory
class NonPersistentHistory(History):

   def load_history_strings(self):
      global HISTORY_DEQUE
      for i in HISTORY_DEQUE:
         yield i

   def store_string(self, string):
      HISTORY_DEQUE.appendleft(string)


class PersistentHistory(FileHistory):

   def __init__(self, name):
      self.history_file = '.%s.history' % name
      FileHistory.__init__(self, self.history_file)