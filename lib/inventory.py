from pyVmomi import vim, Vmodl
from fs import AbstractNode
from constants import MANAGED_ENTITIES

from debug import TestDuration


def FilterType(types):
	ret = ''
	for targetType in types:
		if targetType != vim.Folder:
			for name, type in MANAGED_ENTITIES.items():
				if targetType == type:
					if ret:
						ret += ', '
					ret = name
	return ret.strip()

class Entity(AbstractNode):

	def __init__(self, entity, entity_type, parentFolder):
		AbstractNode.__init__(self)
		self.instance = entity
		self.type = entity_type
		self.name = entity.name
		# self.moid = entity._moid
		self.parent = parentFolder
		self.children = []

	def _get_children(self):
		with TestDuration():
			for attr in dir(self.instance):
				try:
					instance = getattr(self.instance, attr)
					if isinstance(instance, vim.Folder):
						if 'parent' != attr:
							folder = Folder(instance, self)
							self.children.append(folder)
				except Vmodl.fault.MethodNotFound:
					continue

	def get_subs(self):
		if not self.children:
			self._get_children()
		return self.children

	def get_name(self):
		return self.name

	def get_type(self):
		return self.type

	def is_leaf(self):
		if not self.children:
			self._get_children()
		return len(self.children) == 0


class Folder(AbstractNode):

	def __init__(self, folder, parent):
		AbstractNode.__init__(self, parent)
		self.instance = folder
		self.name = ''
		self.type = folder.name
		# self.moid = folder._moid
		self.parent = parent
		self.entitys = []

	def _get_entity(self):
		childTypes = ["UNKNOWN"]
		if hasattr(self.instance, 'childType'):
			childTypes = getattr(self.instance, 'childType')
			entityType = FilterType(childTypes)
		if hasattr(self.instance, 'childEntity'):
			for childInstance in self.instance.childEntity:

				entity = GetEntityFactory().CreateEntity(entityType, childInstance, self)
				if not entity:
					entity = Entity(childInstance, FilterType(childTypes), self)
				self.entitys.append(entity)

	def get_subs(self):
		if not self.entitys:
			self._get_entity()
		return self.entitys

	def get_name(self):
		return self.name

	def set_name(self, name):
		self.name = name

	def get_type(self):
		return self.type

	def is_leaf(self):
		if not self.entitys:
			self._get_entity()
		return len(self.entitys) == 0

class EntityFactory:
	def __init__(self):
		self.entityClasses = {}

	def RegisterEntity(self, key, entityClass):
		if key not in self.entityClasses.keys():
			self.entityClasses[key] = entityClass

	def CreateEntity(self, entity_type, instance, parent):
		if entity_type in self.entityClasses.keys():
			return self.entityClasses[entity_type](instance, entity_type, parent)
		else:
			return Entity(instance, entity_type, parent)

_gEntityFactory = None

def GetEntityFactory():
	global _gEntityFactory
	if _gEntityFactory is None:
		_gEntityFactory = EntityFactory()
	return _gEntityFactory