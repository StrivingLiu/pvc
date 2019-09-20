from HostStub import Host
from VmStub import Vm


def GetHost():
   return Host('stub_host_1', [
      Vm('fake_vm_1', powerState='poweredOff'),
      Vm('fake_vm_2', powerState='poweredOn'),
   ])
