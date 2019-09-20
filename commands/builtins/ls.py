from lib.fs import GetFS
from commands.cmdmanager import GetCmdMgr

def ls(args):
   '''
      {
         'args' : None,
         'desc' : 'list all node'
      }
   '''
   fs = GetFS()
   subNodes = fs.list_subNodes()
   nodeNum = len(subNodes)
   if nodeNum > 0:
      for index, node in zip(range(nodeNum), subNodes):
         print("%-3d  %s (%s)/" % (index, node[0], node[1]))

GetCmdMgr().register_builtin_command('ls', ls)