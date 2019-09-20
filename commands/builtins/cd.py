from lib.fs import GetFS
from lib.prompt import GetPrompt
from commands.cmdmanager import GetCmdMgr

def cd(args):
	'''
      {
         'args' : None,
         'desc' : 'test cd'
      }
	'''
	fs = GetFS()
	if not args or args[0] == '/':
		fs.back_to_root()
	elif args[0] == '..':
		fs.back_one_space()
	elif args[0] == '.':
		pass
	else:
		fs.enter_subNode(args[0])
	GetPrompt().change_path(fs.get_current_path())

GetCmdMgr().register_builtin_command('cd', cd)