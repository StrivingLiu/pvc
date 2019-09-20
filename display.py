import shlex

from lib.prompt import GetPrompt
from lib.constants import InputMode
from commands.cmdmanager import GetCmdMgr

class Interactor:

	def __init__(self, controller):
		self.controller = controller
		self.prompt = GetPrompt()
		self.prompt.add_cmds(GetCmdMgr().generate_prompt())
		self.currentMode = InputMode.NORMAL

	def get_input(self):
		needExit = False
		cmd = self.prompt.get()
		if cmd.strip().lower() == 'exit':
			if self.currentMode == InputMode.DEBUG:
				self.currentMode = InputMode.NORMAL
				cmd = ''
			else:
				needExit = True
		elif cmd.strip().lower() == 'debug':
			self.currentMode = InputMode.DEBUG
			cmd = ''
		return needExit, shlex.split(cmd)

	def generate_output(self):
		pass




