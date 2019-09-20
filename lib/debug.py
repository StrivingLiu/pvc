from time import time, sleep


class TestDuration(object):

	def __init__(self):
		pass

	def __enter__(self):
		self.start = time()

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.end = time()
		print('Running time: {} Seconds'.format(self.end - self.start))


if __name__=="__main__":
	with TestDuration():
		sleep(1)