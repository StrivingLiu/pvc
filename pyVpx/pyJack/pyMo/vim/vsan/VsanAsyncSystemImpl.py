#!/usr/bin/env python

"""
Copyright 2014 VMware, Inc.  All rights reserved. -- VMware Confidential

"""
__author__ = "VMware, Inc"

from pyVmomi import vim, vmodl
from MoManager import GetMoManager
from VsanAsyncSystem import VsanProactiveRebalanceInfo
import os, sys, subprocess, re
import json
from datetime import *
import six

CLOMTOOLCMD = '/usr/lib/vmware/vsan/bin/clom-tool %s'

class VsanAsyncSystemImpl(vim.host.VsanAsyncSystem):
   def VsanAsyncVersion(self):
      return "1.0"

   def _RunCommand(self, cmdStr):
      p = subprocess.Popen(
         cmdStr.split(),
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE)
      (result, errmsg) = p.communicate()
      if p.returncode != 0:
         excepMsg = None
         lines = result.split('\n')
         vobMsgExp = re.compile('^.*vob\.vsan.*\] (.*)$')
         for line in lines:
            vmatch = vobMsgExp.match(line)
            if vmatch:
               excepMsg = vmatch.group(1)
               break
         if excepMsg == None:
            excepMsg = errmsg.replace('\n', ';')
         raise vim.fault.VsanFault(
                faultMessage = \
                [vmodl.LocalizableMessage(message=str(excepMsg))]
               )
      else:
         if six.PY3:
            result = result.decode()
         return result

   '''
   # Start CLOM proactive rebalance by calling clom tool
   '''
   def StartProactiveRebalance(self, timeSpan, varianceThreshold,
                               timeThreshold, rateThreshold):
      if timeSpan == None:
         timeSpan = 86400
      if varianceThreshold == None:
         varianceThreshold = 0.3
      if timeThreshold == None:
         timeThreshold = 1800
      if rateThreshold == None:
         rateThreshold = 51200
      arg = ('start-proactive-rebalance %d %0.2f %d %d' %
         (timeSpan, varianceThreshold, timeThreshold, rateThreshold))
      cmd = (CLOMTOOLCMD % arg)
      self._RunCommand(cmd)
      return True

   '''
   # Stop CLOM proactive rebalance by calling clom tool
   '''
   def StopProactiveRebalance(self):
      cmd = CLOMTOOLCMD % 'stop-proactive-rebalance'
      self._RunCommand(cmd)
      return True

   '''
   # Retrieve CLOM proactive rebalance status by calling clom tool
   '''
   def GetProactiveRebalanceInfo(self):
      cmd = CLOMTOOLCMD % 'info-proactive-rebalance'
      info = json.loads(self._RunCommand(cmd))
      if info['Running']:
         start = datetime.fromtimestamp(info["StartTS"])
         stop = datetime.fromtimestamp(info["StopTS"])
         return vim.host.VsanProactiveRebalanceInfo(
                   running=info["Running"],
                   startTs=start,
                   stopTs=stop,
                   varianceThreshold=info["Variance_Threshold"],
                   timeThreshold=info["Time_Threshold"],
                   rateThreshold=info["Rate_Threshold"]
                )
      else:
         return vim.host.VsanProactiveRebalanceInfo(running=info["Running"])

# Add managed objects during import
GetMoManager().RegisterObjects([VsanAsyncSystemImpl("ha-vsan-async-system")])

