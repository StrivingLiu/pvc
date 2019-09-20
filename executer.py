import traceback
from multiprocessing.managers import BaseManager


def Execute(func, params, context):
	ret = None
	try:
		ret = func(params)
	except Exception as ex:
		ret = traceback.format_exc()
		print(ret)
	finally:
		return ret

class Demo_struct:
	def __init__(self, args=None):
		self.data = args

	def set(self, data):
		self.data = data

	def get(self):
		return self.data



def get_manager():
	manager = BaseManager()
	manager.start()
	return manager

def Init():
	manager = get_manager()
	shared_data = manager.shared_content(args="test")

# BaseManager.register("shared_content", Demo_struct)

if __name__=="__main__":
	pass