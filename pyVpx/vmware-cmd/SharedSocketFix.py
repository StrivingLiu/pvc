# <workaround>
#
# Workaround to make the following error go away:
#
# Exception exceptions.TypeError: "'NoneType' object is not callable"
# in <bound method SharedSocket.__del__ of <httplib.SharedSocket
# instance at 0x8b9b08c>> ignored
#
# We import httplib and then replace its SharedSocket.__del__ method
# with a version that checks the reference count before closing the
# underlying socket object.

import httplib

def SharedSocket__del__(self):
   """
   This function is meant to replace
   httplib.SharedSocket.__del__. This enhanced version checks the reference
   count before closing the underlying socket object and thus prevents the error:

   Exception exceptions.TypeError: "'NoneType' object is not callable"
   in <bound method SharedSocket.__del__ of <httplib.SharedSocket
   instance at 0x8b9b08c>> ignored
   """

   if self._refcnt == 0:
      self.sock.close()

# Replace httplib.SharedSocket.__del__ with enhanced version
try:
   globals()['httplib'].SharedSocket.__del__ = SharedSocket__del__
except: pass

# </workaround>
