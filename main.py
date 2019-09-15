import sys
import traceback

from controller import Controller
from executer import Execute
from display import Interactor


def Exit(status=1):
	sys.exit(status)

def Run():
	data = None
	controller = Controller(Execute, data)
	interactor = Interactor(controller)
	try:
		while True:
			exit, cmd = interactor.get_input()
			if exit:
				Exit()
			else:
				controller.run_cmd(cmd)
				#interactor.generate_output()
	except KeyboardInterrupt:
		Exit()
	except Exception as e:
		exstr = traceback.format_exc()
		Exit()



if __name__=="__main__":
	Run()