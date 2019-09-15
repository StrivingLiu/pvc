import traceback

from lib.prompt import Prompt
from constants import InputMode


class Interactor:

	def __init__(self, controller):
		self.controller = controller
		self.prompt = Prompt()
		self.currentMode = InputMode.NORMAL

	def get_input(self):
		needExit = False
		cmd = self.prompt.Get()
		if cmd.strip().lower() == 'exit':
			if self.currentMode == InputMode.DEBUG:
				self.currentMode = InputMode.NORMAL
				cmd = ''
			else:
				needExit = True
		elif cmd.strip().lower() == 'debug':
			self.currentMode = InputMode.DEBUG
			cmd = ''
		return needExit, cmd

	def generate_output(self):
		pass




