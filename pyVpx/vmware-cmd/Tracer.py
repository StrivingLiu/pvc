import inspect
import sys

def Activate():
   sys.settrace(Tracer().TraceFunc)


class Tracer(object):

   def __init__(self):
      self.level = 0

   def TraceFunc(self, frame, event, arg):
      #if frame.f_code.co_filename != __file__: return

      method = getattr(self, 'on_%s' % event, None)
      if method: method(frame, event, arg)

      return self.TraceFunc

   @staticmethod
   def _IsString(obj):
      try:
         obj.lower()
      except:
         return False
      else:
         return True

   @staticmethod
   def _FormatReturnValue(arg):
      if Tracer._IsString(arg):
         return '"%s"' % arg
      elif type(arg) == type(None):
         return 'None'
      elif type(arg) == type((1, 2)):
         return str(arg)
      else:
         return str(type(arg))

   def _PrintLevel(self, arg):
      print('# %s%s' % (3 * self.level * ' ', arg))

   def on_call(self, frame, event, arg):
      # This is a hack to prevent a SEGV that I was seeing when
      # Vm.__init__ gets called with tracing on.
      if frame.f_code.co_name == '__init__': return
      argvalues = inspect.getargvalues(frame)
      self._PrintLevel('%s%s' %
                       (frame.f_code.co_name,
                        inspect.formatargvalues(*argvalues)))
      self.level += 1

   def on_return(self, frame, event, arg):
      self._PrintLevel('return ' + Tracer._FormatReturnValue(arg))
      self.level -= 1

   def on_exception(self, frame, event, arg):
      self._PrintLevel('* exception ' + Tracer._FormatReturnValue(arg))
