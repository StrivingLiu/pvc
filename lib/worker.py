import time
import multiprocessing

class Worker:
	def __init__(self, execute_func, shared_data):
		self.data = shared_data
		self.execute_func = execute_func
		self.check_func = None
		self._create_pool()

	def _create_pool(self, num=1):
		self.work_pool = multiprocessing.Pool(processes=num)

	def run(self, cmd, params):
		if self.work_pool is None:
			self._create_pool()
		result=self.work_pool.apply_async(self.execute_func,
		                                  (cmd, params, self.data))
		ret = ''
		while True:
			try:
				ret = result.get(timeout=1)
				break
			except multiprocessing.context.TimeoutError:
				if self.check_func:
					if True != self.check_func():
						self.force_stop()
						ret = 'interrupt!'
						break
				continue
		print("Result: %s" % ret)

	def stop(self):
		if self.work_pool:
			self.work_pool.close()
			self.work_pool.join()

	def force_stop(self):
		if self.work_pool:
			self.work_pool.terminate()
			self.work_pool = None

	def set_checkFunc(self, func):
		self.check_func = func


#########################################################

def test_worker(str="aaa"):
	time.sleep(3)
	name = multiprocessing.current_process().name
	print(name + '-' + str)
	return name

def test_execute(cmd, params, data):
	cmd(**params)

#########################################################

if __name__=="__main__":
	state = True
	def test_get_state():
		return state
	data = None
	worker = Worker(test_execute, data)
	worker.set_checkFunc(test_get_state)
	worker.run(test_worker, {'str': "test_worker"})
	print("Mock: interrupt")
	state = False
	worker.run(test_worker, {'str': "test_worker_1"})
	worker.stop()