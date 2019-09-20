import sys, traceback

"""
Utility functions
"""

def printWithPrefix(str, prefix='# '):
   print '\n'.join(['%s%s' % (prefix, line) for line in str.splitlines()])

def rec_getattr(obj, name, default=None):
   try:
      return  reduce(getattr, name.split('.'), obj)
   except AttributeError, e:
      raise AttributeError, 'Invalid attribute: \'%s\'' % name

def FirstTrue(iterable, predicate=None):
   if predicate is None:
      predicate = bool
   for x in iterable: 
      if predicate(x): return x

memoizedData = {}

def memoize(origFunc):
   def _func(*args, **kwargs):
      #print 'args = %s' % args
      cacheKey = ','.join([repr(arg) for arg in [origFunc] + list(args) + list(kwargs)])
      #print '*** Memoized: cacheKey = "%s"' % cacheKey
      if memoizedData.get(cacheKey, None) is None:
         #print '* not in cache *'
         memoizedData[cacheKey] = origFunc(*args, **kwargs)

      return memoizedData[cacheKey]

   return _func

def IsPyVmomiException(e):
   return IsFromPyVmomiModule(e)

def IsPyVmomiTask(obj):
   return type(obj).__name__ == 'vim.Task'

def IsFromPyVmomiModule(aType):
   return hasattr(aType, '__module__') and \
          aType.__module__.startswith('pyVmomi')
