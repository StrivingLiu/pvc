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
	def __init__(self):
		self.currentNode = None
		self.subNodes = []

	def setup(self, rootNode):
		self.rootNode = rootNode
		self.currentNode = rootNode

	def _change_dir(self, node):
		self.currentNode = node
		self.subNodes = []

	def get_current_path(self):
		return self.currentNode.get_path()

	def list_subNodes(self):
		if not self.subNodes:
			self.subNodes = self.currentNode.get_subs()
		nodesName = [(node.get_name(), node.get_type(),) for node in self.subNodes]
		return nodesName

	def enter_subNode(self, params):
		if not params:
			return
		try:
			if len(params) == 1 and params[0].isdigit():
				self._change_dir(self.subNodes[int(params[0])])
			else:
				exist = False
				for node in self.subNodes:
					if params[0] == node.get_name():
						exist = True
						self._change_dir(node)
						break
				if not exist:
					pass
		except IndexError:
			print('no matches for "%s"' % params[0])

	def back_to_root(self):
		self._change_dir(self.rootNode)

	def back_one_space(self):
		self._change_dir(self.currentNode.parent)

	def get_info(self, node):
		pass

_gFileSystem = None
def GetFS():
	global _gFileSystem
	if not _gFileSystem:
		_gFileSystem = FS()
	return _gFileSystem
