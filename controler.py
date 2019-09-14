import signal

from lib import Worker

class Controler(object):
	NEED_EXIT = False
	SIGNAL_HANDLE = None

	def __init__(self, data):
		if not Controler.SIGNAL_HANDLE:
			Controler.signal_init()
			Controler.SIGNAL_HANDLE = Controler.interrupt_handler
		self.worker = Worker(data)
		self.worker.set_checkFunc(self.get_state)

	def get_state(self):
		return Controler.NEED_EXIT

	@classmethod
	def interrupt_handler(cls, signum, frame):
		cls.NEED_EXIT = True

	@classmethod
	def signal_init(cls):
		signal.signal(signal.SIGINT, cls.interrupt_handler)
		signal.signal(signal.SIGTERM, cls.interrupt_handler)

if __name__=="__main__":
	pass