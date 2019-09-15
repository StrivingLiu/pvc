


class AbstractCommand:

	def __init__(self):
		pass



class CommandManager:

	def __init__(self):
		self.builtInCommands = {}

	def register_builtin_command(self, name, func):
		self.builtInCommands[name] = func
