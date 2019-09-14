import sys
import os
import re
import json
import socket
import ssl
import inspect

import pyVim
import pyVim.connect
import pyVim.task
from pyVmomi import vim, Vmodl

from copy import copy
from fs import AbstractNode

PORT=443

def PyVimConnect(host, user='Administrator@vsphere.local', pwd='Admin!23',
                 version='vim.version.version11'):
	context = None
	if sys.version_info >= (3, 0):
		context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
	elif getattr(ssl, '_create_unverified_context', None):
		ssl._create_default_https_context = ssl._create_unverified_context
	return pyVim.connect.Connect(host=host, user=user, pwd=pwd,
                               version=version, sslContext=context)

def get_entity_subfolder(entity):
	ret = []
	index = 0
	if entity:
		for attr in dir(entity):
			instance = getattr(entity, attr)
			if isinstance(instance, vim.Folder):
				moId = instance._moId
				folder = Folder(moId, instance, attr, index)
				if hasattr(instance, 'name'):
					folder.set_name(instance.name)
				folder.set_depth(depth)
				index += 1
				ret.append(folder)
	return ret

class Entity(AbstractNode):

	def __init__(self, entity, type, parentFolder):
		AbstractNode.__init__(self)
		self.instance = entity
		self.types = type
		self.name = entity.name
		self.moid = entity._moid
		self.parent = parentFolder
		self.subFolders = []

	def _get_subFolders(self):
		for attr in dir(self.instance):
			instance = getattr(self.instance, attr)
			if isinstance(instance, vim.Folder):
				if 'parent' != instance.name:
					folder = Folder(instance, self.instance)
					self.subFolders.append(folder)

	def get_subs(self):
		if not self.subFolders:
			self._get_subFolders()
		return self.subFolder

	def get_name(self):
		return self.name

	def get_type(self):
		return self.types

	def is_leaf(self):
		if not self.subFolders:
			self._get_subFolder()
		return len(self.subFolders) == 0


class Folder(AbstractNode):

	def __init__(self, folder, parentEntity):
		AbstractNode.__init__(self, parentEntity)
		self.instance = folder
		self.name = folder.name
		self.moid = folder._moid
		self.parent = parentEntity
		self.entitys = []

	def _get_entity(self):
		childTypes = ["UNKNOWN"]
		if hasattr(self.instance, 'childType'):
			childTypes = getattr(self.instance, 'childType')
		if hasattr(self.instance, 'childEntity'):
			for childInstance in self.instance.childEntity:
				entity = Entity(childInstance, copy(childTypes), self.instance)
				self.entitys.append(entity)

	def get_subs(self):
		if not self.entitys:
			self._get_entity()
		return self.entitys

	def get_name(self):
		return self.name

	def get_type(self):
		return ''

	def is_leaf(self):
		if not self.entitys:
			self._get_entity()
		return len(self.entitys) == 0