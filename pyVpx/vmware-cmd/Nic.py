from Utils import rec_getattr


class Nic(object):
   """
   Wraps a Nic ManagedObject and adds some methods and
   properties for convenience.
   """

   def __init__(self, managedObject):
      self.managedObject = managedObject

   @property
   def connected(self):
      return self.managedObject.connected

   @property
   def deviceConfigId(self):
      return self.managedObject.deviceConfigId

   @property
   def ipAddress(self):
      return ', '.join(self.managedObject.ipAddress)
      """
      ipAddresses = self.managedObject.ipAddress
      if len(ipAddresses) <= 1:
         return ipAddresses[0]
      else:
         return ipAddresses
      """

   @property
   def macAddress(self):
      return self.managedObject.macAddress

   @property
   def network(self):
      return self.managedObject.network

   @property
   def quotedNetwork(self):
      return '"%s"' % self.network

   def __eq__(self, other):
      return (self.connected == other.connected and
              self.deviceConfigId == other.deviceConfigId and
              self.ipAddress == other.ipAddress and
              self.macAddress == other.macAddress and
              self.network == other.network)
