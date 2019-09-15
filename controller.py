import signal

from lib import Worker

class Controller(object):
	NEED_EXIT = False
	SIGNAL_HANDLE = None

	def __init__(self, exec, data):
		if not Controller.SIGNAL_HANDLE:
			Controller.signal_init()
			Controller.SIGNAL_HANDLE = Controller.interrupt_handler
		self.worker = Worker(exec, data)
		self.worker.set_checkFunc(self.get_state)

	def get_state(self):
		return Controller.NEED_EXIT

	def run_cmd(self, cmd):
		self.worker.run(cmd, None)

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