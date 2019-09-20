#!/usr/bin/env python3
import os
import sys
import argparse


if sys.version_info < (2, 7):
   raise Exception('Only supports python versions after 2.7')

filePath = os.path.abspath(__file__)


sys.path.append(os.path.join(os.path.dirname(filePath), 'lib'))
sys.path.append(os.path.join(os.path.dirname(filePath), 'pyVpx'))
from commands.builtins import *
from lib.connect import PyVimConnect
from lib.inventory import Folder
from lib.extensions import *
from lib.fs import GetFS

def Connect_to_vc(vc_ip):
   try:
      si = PyVimConnect(vc_ip)
      GetFS().setup(Folder(si.content.rootFolder, None))
   except Exception as ex:
      raise Exception('invalid vc ip')

def GetInput():
   parser = argparse.ArgumentParser()
   parser.add_argument("vc_ip", help="VC IP address")
   getArgs = parser.parse_args()
   if not getArgs.vc_ip:
      parser.print_usage()
      sys.exit(0)
   return getArgs.vc_ip

def Init():
   vc_ip = GetInput()
   Connect_to_vc(vc_ip)