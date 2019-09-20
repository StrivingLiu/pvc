import signal

from lib.worker import Worker
from commands.cmdmanager import GetCmdMgr
from executer import Execute

class Controller(object):
	NEED_EXIT = False
	SIGNAL_HANDLE = None

	def __init__(self, func, data):
		if not Controller.SIGNAL_HANDLE:
			Controller.signal_init()
			Controller.SIGNAL_HANDLE = Controller.interrupt_handler
		self.cmdMgr = GetCmdMgr()
		self.worker = Worker(func, data)
		self.worker.set_checkFunc(self.get_state)

	def get_state(self):
		return Controller.NEED_EXIT

	def run_cmd(self, cmd):
		func = self.cmdMgr.get_cmd(cmd[0])
		if not func:
			print('Invalid command')
			return
		if self.cmdMgr.is_builtin_cmd(cmd[0]):
			Execute(func, cmd[1:], None)
		else:
			self.worker.run(func, cmd[1:])

	def get_output(self):
		pass

	@classmethod
	def interrupt_handler(cls, signum, frame):
		cls.NEED_EXIT = True

	@classmethod
	def signal_init(cls):
		signal.signal(signal.SIGINT, cls.interrupt_handler)
		signal.signal(signal.SIGTERM, cls.interrupt_handler)

if __name__=="__main__":
	pass