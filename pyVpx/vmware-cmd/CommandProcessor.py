class InvalidOperation(Exception): pass

class InvalidParameter(Exception): pass

import operations, sys, Utils


def Process(host, args):
   result = None
   operation = _GetOperationFromArgs(args)
   if not operation: raise InvalidOperation()

   try:
      processedArgs = [host] + _ProcessArgs(host, args)
      result = operation.DoIt(*processedArgs)
   except Exception, e:
      """
      Question: Why catch Exception and then check for a specific
      exception type? Why not have separate catch clauses?

      Answer: I can avoid importing pyVmomi and coupling to it.
      """

      if Utils.IsPyVmomiException(e):
         sys.stderr.write('%s: %s\n'
                          % (e.__class__.__name__, getattr(e, 'msg', None) or e))
      else:
         raise

   return operation.name, result


def _GetOperationFromArgs(args):
   for arg in args:
      opClass = operations.GetOperationByName(arg)
      if opClass: return opClass


def _ProcessArgs(host, args):
   return [ arg for arg in args if not operations.GetOperationByName(arg) ]


def _Process1Arg(host, arg):
   return host.GetVm(arg)

