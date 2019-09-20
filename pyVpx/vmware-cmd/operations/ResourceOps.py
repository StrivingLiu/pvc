import pyVmomi
from Operation import Operation


class SetResource(Operation):

   usage = '<variable> <value>'
   notes = '(Not implemented)'
   hidden = True

   def DoIt(self, host, *args):
      if len(args) >= 3:
         return self.VmOperation(host, *args)
      else:
         return self.ServerOperation(host, *args)

   def VmOperation(self, host, vm, variable, value):
      print('### SetResource.VmOperation: vm = %s; variable = "%s"; value = "%s"'
            % (vm, variable, value))

   def ServerOperation(self, host, variable, value):
      print('### SetResource.ServerOperation: variable = "%s"; value = "%s"'
            % (variable, value))


class GetResource(Operation):

   """
   Examples of usage of old tool:

   # Vm operations:

   pivot02:/# vmware-cmd -s getresource system.disk.HTL
   getresource(system.disk.HTL) = vmhba0:0:0

   pivot02:/# vmware-cmd -H pioneer-131.eng.vmware.com \
   > -U root -P 'passwd' \
   > '/vmfs/volumes/44ee4eb7-28601011-5305-000e0c6dbc76/VirtualCenter 2.5 VM/VirtualCenter 2.5 VM.vmx' \
   > getresource disk.HTL
   getresource(disk.HTL) = vmhba1:0:0

   pivot02:/# vmware-cmd \
   > /vmfs/volumes/457d7a7c-01488e38-480b-003048322058/Jai-ESX-88796/Jai-ESX-88796.vmx \
   > getresource disk.vmhba0:0:0.KBread
   getresource(disk.vmhba0:0:0.KBread) = 458310

   # Server operations:

   pivot02:/tmp/control-only# vmware-cmd -s getresource system.disk.HTL
   getresource(system.disk.HTL) = vmhba0:0:0
   pivot02:/tmp/control-only# vmware-cmd -s getresource system.disk.vmhba0:0:0.KBread
   getresource(system.disk.vmhba0:0:0.KBread) = 1399342889

   Examples of usage of new tool:

   $ vmware-cmd2 -H pivot02 -s getresource system.mem.active
   getresource(system.mem.active) = 241500

   @todo Add more examples here...
   """

   usage = '<variable>'
   notes = '(Not completely implemented yet?)'
   hidden = True

   def DoIt(self, host, *args):
      if len(args) >= 2:
         vm = Operation.GetVm(host, args[0])
         entity = vm.managedObject
         variable = args[-1]
         instance = variable.split('.')[-2]
      else:
         entity = host.hostSystem
         variable = args[-1]
         instance = ''

      return self.GetResourceHelper(host, entity, instance, variable)

   def GetCounterId(self, perfManager, variable):
      if variable.isdigit():
         return int(variable)

      stat = variable.split('.')[-1]
      if stat.isdigit(): return int(stat)

      # This map derived from bora/lib/vmcontrol/DataMap.txt
      perfMetricMap = {
         "active":       ( "mem", "active", "KB", "average" ),
         "avail":        ( "mem", "unreserved", "KB", "average" ),
         "memctl":       ( "mem", "vmmemctl", "KB", "average" ),
         "overhd":       ( "mem", "overhead", "KB", "average" ),
         "ovhdmax":      ( "mem", "overhead", "KB", "maximum" ),
         "shared":       ( "mem", "shared", "KB", "average" ),
         "sharedCommon": ( "mem", "sharedcommon", "KB", "average" ),
         "size":         ( "mem", "granted", "KB", "average" ),
         "swapped":      ( "mem", "swapused", "KB", "average" ),
         "zero":         ( "mem", "zero", "KB", "average" ),
         "max":          ( "mem", "granted", "KB", "maximum" ),
         "min":          ( "mem", "granted", "KB", "minimum" ),
         "reservedMem":  ( "mem", "reservedCapacity", "MB", "average" ),
         "sysHeapSize":  ( "mem", "heap", "KB", "average" ),
         "emin":         ( "cpu", "guaranteed", "millisecond", "latest" ),
         "extrasec":     ( "cpu", "extra", "millisecond", "summation" ),
         "syssec":       ( "cpu", "system", "millisecond", "summation" ),
         "ready":        ( "cpu", "ready", "millisecond", "summation" ),
         "usedsec":      ( "cpu", "used", "millisecond", "summation" ),
         "waitsec":      ( "cpu", "wait", "millisecond", "summation" ),
         "active":       ( "mem", "active", "kiloBytes", "average" ),
         "mctltgt":      ( "mem", "vmmemctltarget", "kiloBytes", "average" ),
         "memctl":       ( "mem", "vmmemctl", "kiloBytes", "average" ),
         "overhd":       ( "mem", "overhead", "kiloBytes", "average" ),
         "ovhdmax":      ( "mem", "overhead", "kiloBytes", "maximum" ),
         "shared":       ( "mem", "shared", "kiloBytes", "average" ),
         "size":         ( "mem", "granted", "kiloBytes", "average" ),
         "swapin":       ( "mem", "swapin", "kiloBytes", "average" ),
         "swapout":      ( "mem", "swapout", "kiloBytes", "average" ),
         "swapped":      ( "mem", "swapped", "kiloBytes", "average" ),
         "swaptgt":      ( "mem", "swaptarget", "kiloBytes", "average" ),
         "zero":         ( "mem", "zero", "kiloBytes", "average" ),
         "KBread":       ( "disk", "read", "kiloBytesPerSecond", "average" ),
         "KBwritten":    ( "disk", "write", "kiloBytesPerSecond", "average" ),
         "reads":        ( "disk", "numberRead", "number", "summation" ),
         "writes":       ( "disk", "numberWrite", "number", "summation" ),
         "phyKBRx":      ( "net", "received", "kiloBytesPerSecond", "average" ),
         "phyKBTx":      ( "net", "transmitted", "kiloBytesPerSecond", "average" ),
         "phyPktsRx":    ( "net", "packetsRx", "number", "summation" ),
         "phyPktsTx":    ( "net", "packetsTx", "number", "summation" ),
         "totKBRx":      ( "net", "received", "kiloBytesPerSecond", "average" ),
         "totKBTx":      ( "net", "transmitted", "kiloBytesPerSecond", "average" ),
         "totPktsRx":    ( "net", "packetsRx", "number", "summation" ),
         "totPktsTx":    ( "net", "packetsTx", "number", "summation" ),
         }

      groupInfoKey, nameInfoKey, unitInfoKey, rollupType = perfMetricMap[stat]

      #print('stat = %s; groupInfoKey = %s; nameInfoKey = %s; unitInfoKey = %s; rollupType = %s'
      #      % (stat, groupInfoKey, nameInfoKey, unitInfoKey, rollupType))

      def _Matches(rec):
         if rec.groupInfo.key != groupInfoKey: return False
         if rec.nameInfo.key  != nameInfoKey:  return False
         if rec.unitInfo.key  != unitInfoKey:  return False
         if rec.rollupType    != rollupType:   return False
         return True

      for rec in perfManager.perfCounter:
         if _Matches(rec): return rec.key

   def GetCounterById(self, perfManager, entity, instance, counterId):
      #printWithPrefix('GetCounterById: counterId = %s' % counterId)

      metricId = pyVmomi.Vim.PerformanceManager.MetricId(counterId=counterId, instance=instance)

      #printWithPrefix('GetCounterById: metricId = %s' % metricId)

      ret = perfManager.QueryStats([
            pyVmomi.Vim.PerformanceManager.QuerySpec(entity=entity,
                                  maxSample=1,
                                  intervalId=0,
                                  metricId=[metricId]
                                  )])

      #printWithPrefix('GetCounterById: ret = %s' % ret)

      try:    return int(ret[0].value[0].value[0])
      except: return None

   def GetResourceHelper(self, host, entity, instance, variable):
      perfManager = host.perfManager
      counterId = self.GetCounterId(perfManager, variable)

      #printWithPrefix('GetResourceHelper: variable = %s; counterId = %s'
      #                % (variable, counterId))

      return self.GetCounterById(perfManager, entity, instance, counterId)


class GetHostPerfCounter(Operation):

   hidden = True
   usage = '<counterId>'

   def DoIt(self, host, counterId):
      """
      Example:

      $ ./vmware-cmd2 -H pivot02 -s gethostperfcounter 65545
      gethostperfcounter(65545) = 461704
      """

      perfManager = host.perfManager

      #print('GetHostPerfCounter.DoIt: counterId = %s' % (counterId))

      entity = host.hostSystem
      metricId = pyVmomi.Vim.PerformanceManager.MetricId(counterId=int(counterId),
                                      instance='')

      ret = perfManager.QueryStats([
            pyVmomi.Vim.PerformanceManager.QuerySpec(entity=entity,
                                  maxSample=1,
                                  intervalId=0,
                                  metricId=[metricId]
                                  )])
      #print(ret)

      try:    return int(ret[0].value[0].value[0])
      except: return None



class ListPerfCounters(Operation):

   hidden = True
   usage = ''

   def DoIt(self, host):
      """
      Example:

      $ ./vmware-cmd2 -H pioneer-131 listperfcounters | egrep 'cpu\.usage'
             0: cpu.usage.none (rate percent)
             1: cpu.usage.average (rate percent)
             2: cpu.usage.maximum (rate percent)
             3: cpu.usage.minimum (rate percent)
             4: cpu.usagemhz.none (rate megaHertz)
             5: cpu.usagemhz.average (rate megaHertz)
             6: cpu.usagemhz.maximum (rate megaHertz)
             7: cpu.usagemhz.minimum (rate megaHertz)
      """

      perfManager = host.perfManager

      res = ["%8d: %s.%s.%s (%s %s)"
             % (c.key, c.groupInfo.key, c.nameInfo.key,
                c.rollupType, c.statsType, c.unitInfo.key)
             for c in perfManager.perfCounter]
      res.sort()
      #print "\n".join(res)
      return res
