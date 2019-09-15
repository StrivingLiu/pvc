from connect import get_entity_subfolder

import os

class AbstractNode:

	def __init__(self, parentNode=None):
		self.parent = parentNode

	def get_subs(self):
		return []

	def get_name(self):
		return ''

	def get_type(self):
		return 'UNKNOWN'

	def get_path(self):
		path = '/'
		if self.parent:
			path = self.parent.get_path()
			path = os.path.join(path, self.get_name())
		return path

	def create_sub(self):
		pass

	def is_leaf(self):
		return True


class FS:
	def __init__(self, rootNode):
		self.rootNode = rootNode
		self.currentNode = rootNode
		self.subNodes = []

	def get_current_path(self):
		return self.currentNode.get_path()

	def list_subNodes(self):
		if not self.subNodes:
			self.subNodes = self.currentNode.get_subs()
		nodesName = [(node.get_name(), node.get_type(),) for node in self.subNodes]
		return nodesName

	def enter_subNode(self, index):
		if index.isdigit():
			self.currentNode = self.subNodes[int(index)]
		else:
			exist = False
			for node in self.subNodes:
				if index == node.get_name():
					exist = True
					self.currentNode = node
					break
			if not exist:
				pass

if __name__=="__main__":
	from connect import PyVimConnect, Entity, Folder

	try:
		si = PyVimConnect('10.192.231.51')
	except Exception as ex:
		raise Exception('invalid vc ip')
	fs = FS(Folder(si.content.rootFolder, None))
	print(fs.get_current_path())
	print(fs.list_subNodes())


	"""
	""
	ls: folder; 0 Datacenters(no)
	cd: 0
	"/Datacenters"
	ls: entity; 0 VSAN_SCALE_DC(Datacenter)
	cd: 0
	(/VSAN_SCALE_DC)
	"/Datacenters/VSAN_SCALE_DC"
	ls: folder; 0 host(); 1 network();2 vm()
	cd: 0
	"/Datacenters/VSAN_SCALE_DC/host"
	ls: entity; 0 cluster_1(computeResource); 1 cluster_2(computeResource) 
	cd: 0
	(/VSAN_SCALE_DC/cluster_1)
	"/Datacenters/VSAN_SCALE_DC/host/cluster_1"
	ls: 
	"""