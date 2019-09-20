#!/usr/bin/python

import sys
import getopt
from pyVmomi import Vim
from pyVim.connect import Connect, Disconnect
from pyVim.task import WaitForTask
from pyVim import vm, folder, invt
from pyVim import vmconfig
from pyVim import arguments
from pyVim.helpers import Log,StopWatch
import atexit

## Cleanup existing VMs with given name
def CleanupVm(vmname):
    vm1 = folder.Find(vmname)
    if vm1 != None:
        Log("Cleaning up VM " + vmname)
        vm.Destroy(vm1)

## Check the VM's config for disks
def CheckForDisk(vm1, numDev, scrubbed = True):
    if scrubbed == True:
        param = {"backing.eagerlyScrub": True}
    else:
        param = {}

    devType = Vim.Vm.Device.VirtualDisk
    devices = vmconfig.CheckDevice(vm1.GetConfig(), devType)

    if len(devices) != numDev:
        raise Exception("Failed to find %d disks" % numDev)
    else:
        Log("Verified VM device configuration")
    return devices

def main():
   supportedArgs = [ (["h:", "host="], "localhost", "Host name", "host"),
                     (["u:", "user="], "root", "User name", "user"),
                     (["p:", "pwd="], "ca$hc0w", "Password", "pwd"),
                     (["v:", "vmname="], "Hw7ReconfigTest", "Name of the virtual machine", "vmname"),
                     (["i:", "numiter="], "1", "Number of iterations", "iter") ]

   supportedToggles = [ (["usage", "help"], False, "Show usage information", "usage"),
                        (["runall", "r"], True, "Run all the tests", "runall"),
                        (["nodelete"], False, "Dont delete vm on completion", "nodelete") ]

   args = arguments.Arguments(sys.argv, supportedArgs, supportedToggles)
   if args.GetKeyValue("usage") == True:
      args.Usage()
      sys.exit(0)

   # Connect
   si = Connect(host=args.GetKeyValue("host"),
                user=args.GetKeyValue("user"),
                pwd=args.GetKeyValue("pwd"),
                version="vim.version.version9")
   atexit.register(Disconnect, si)


   # Process command line
   vmname = args.GetKeyValue("vmname")
   numiter = int(args.GetKeyValue("iter"))
   runall = args.GetKeyValue("runall")
   noDelete = args.GetKeyValue("nodelete")
   status = "PASS"

   for i in range(numiter):
       bigClock = StopWatch()
       vm1 = None
       try:
           ## Cleanup old VMs
           posVmName = vmname + "_Pos_" + str(i)
           CleanupVm(posVmName)

           ## Create a hwVersion 7 VM with a flat (non-scrubbed disk)
           Log("Creating Hw7 VM..")
           vm1 = vm.CreateQuickDummy(posVmName, 1, 0,
                                     vmxVersion = "vmx-07",
                                     diskSizeInMB = 80)
           Log("Created VM")

	   # Add a thin-provisioned disk to the VM
	   cspec = Vim.Vm.ConfigSpec()
	   cspec = vmconfig.AddDisk(cspec, cfgInfo = vm1.GetConfig(), thin = True,
                                    capacity = 80 * 1024)
	   vm.Reconfigure(vm1, cspec)
	   Log("VM reconfigured to have a thin disk")
           devices = CheckForDisk(vm1, 2, False)

	   # Reconfigure the VM to convert its disks to eager-zeroed thick
	   cspec = Vim.Vm.ConfigSpec()
	   for disk in devices:
	       backing = disk.GetBacking()
	       backing.SetEagerlyScrub(True)
	       disk.SetBacking(backing)
	       vmconfig.AddDeviceToSpec(cspec, disk, Vim.Vm.Device.VirtualDeviceSpec.Operation.edit)
	   vm.Reconfigure(vm1, cspec)
	   Log("VM reconfigured successfully to have eager-zeroed disks")
           CheckForDisk(vm1, 2)

           Log("Powering on VM")
           vm.PowerOn(vm1)

           Log("Adding scrubbed disk to VM")
           cspec = Vim.Vm.ConfigSpec()
	   cspec = vmconfig.AddDisk(cspec, cfgInfo = vm1.GetConfig(), scrub = True,
                                    capacity = 80 * 1024)
           vm.Reconfigure(vm1, cspec)
           CheckForDisk(vm1, 3)

           Log("Powering off VM")
           vm.PowerOff(vm1)

           Log("Destroying VM")
           vm.Destroy(vm1)

           Log("Tests completed.")
           bigClock.finish("iteration " + str(i))
       except Exception as e:
           status = "FAIL"
           Log("Caught exception : " + str(e))
   Log("TEST RUN COMPLETE: " + status)


# Start program
if __name__ == "__main__":
    main()
