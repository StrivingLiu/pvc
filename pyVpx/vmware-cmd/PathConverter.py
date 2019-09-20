import re
import os


class PathConverter(object):
   """
   An object that can convert back and forth between datastore paths
   and local paths.

   I wonder if this should be moved into pyVim?
   """

   def __init__(self, datastoreList):
      """
      @param datastoreList List of datastores (i.e..: HostSystem.datastore)
      """

      self._regex1 = re.compile(r'^\[(?P<dsName>[^\]]+)\] (?P<path>.*)')
      self._regex2 = re.compile(r'^(?P<dsUrl>/vmfs/volumes/[^/]+)/(?P<path>.*)')
      self._dsNameToUrlMap, self._dsUrlToNameMap = {}, {}

      for datastore in datastoreList:
         self._dsNameToUrlMap[datastore.info.name] = datastore.info.url
         self._dsUrlToNameMap[datastore.info.url] = datastore.info.name
         self._dsUrlToNameMap['/vmfs/volumes/%s' % datastore.info.name] = datastore.info.name

   def GetLocalPathFromDsPath(self, dsPath):
      """
      Get a local path
      (e.g.: "/vmfs/volumes/44ee4eb7-28601011-5305-000e0c6dbc76/vm1/vm1.vmx")
      from a datastore path (e.g.: "[storage1] vm1/vm1.vmx")
      """

      match = self._regex1.search(dsPath)
      if match:
         dsUrl = self._GetDsUrl(match.group('dsName'))
         return match.expand(r'%s/\g<path>' % dsUrl)
      else:
         return dsPath

   def GetDsPathFromLocalPath(self, localPath):
      """
      Get a datastore path (e.g.: "[storage1] vm1/vm1.vmx")
      from a local path
      (e.g.: "/vmfs/volumes/44ee4eb7-28601011-5305-000e0c6dbc76/vm1/vm1.vmx")
      """

      if (os.path.isfile(localPath)):
         localPath = os.path.abspath(localPath)
      match = self._regex2.search(localPath)
      if match:
         dsName = self._GetDsName(match.group('dsUrl'))
         return match.expand(r'[%s] \g<path>' % dsName)
      else:
         return localPath

   def _GetDsUrl(self, dsName):
      return self._dsNameToUrlMap[dsName]

   def _GetDsName(self, dsUrl):
      return self._dsUrlToNameMap[dsUrl]
