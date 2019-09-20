

class AbstractCommand:

	def __init__(self):
		pass

class CommandManager:

	def __init__(self):
		self.builtInCommands = {}

	def register_builtin_command(self, name, func):
		self.builtInCommands[name] = func

	def generate_prompt(self):
		cmdPrompt = {}
		for name, method in self.builtInCommands.items():
			if method.__doc__ is not None:
				strs = ''
				for line in method.__doc__.split('\n'):
					strs += line.lstrip()
				try:
					obj = eval(strs)
				except:
					print('error!')
				else:
					cmdPrompt[name] = obj
		return cmdPrompt

	def is_builtin_cmd(self, cmd_name):
		return cmd_name in self.builtInCommands

	def get_cmd(self, cmd_name):
		if cmd_name in self.builtInCommands:
			return self.builtInCommands[cmd_name]
		else:
			return None

_gCmdMgr = CommandManager()

def  GetCmdMgr():
	return _gCmdMgr