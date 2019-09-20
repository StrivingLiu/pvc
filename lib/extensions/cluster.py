from lib.inventory import Entity

class Cluster(Entity):

	def __init__(self, entity, types, parentFolder):
		Entity.__init__(self, entity, types, parentFolder)

	def _get_children(self):
		hosts = self.instance.host
		for host in hosts:
			entity = Entity(host, 'host', self)
			self.subFolders.append(entity)