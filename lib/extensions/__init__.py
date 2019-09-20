from lib.inventory import GetEntityFactory
from lib.extensions.datacenter import Datacenter

GetEntityFactory().RegisterEntity('datacenter', Datacenter)