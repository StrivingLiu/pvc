from lib.inventory import Entity, Folder
from pyVmomi import Vmodl
from lib.debug import TestDuration

# class TestDuration(object):
#
# 	def __init__(self):
# 		pass
#
# 	def __enter__(self):
# 		self.start = time.time()
#
# 	def __exit__(self, exc_type, exc_val, exc_tb):
# 		self.end = time.time()
# 		print('Running time: {} Seconds'.format(self.end - self.start))

CHILD_PROPERTY = {
	'type' : 'Folder',
	'child' : {
		'hostFolder': 'computers',
		'networkFolder' : 'networks',
		'datastoreFolder' : 'datastores',
		'vmFolder': 'vms',
	}
}

class Datacenter(Entity):

	def __init__(self, entity, types, parentFolder):
		Entity.__init__(self, entity, types, parentFolder)

	def _get_children(self):
		with TestDuration():
			for childName, typeName in CHILD_PROPERTY['child'].items():
				try:
					instance = getattr(self.instance, childName, None)
					if instance:
						folder = Folder(instance, self)
						folder.set_name(typeName)
						self.children.append(folder)
				except Vmodl.fault.MethodNotFound:
					continue
