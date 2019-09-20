#!/usr/bin/env python

"""
Run unit tests in *Tests.py
"""

import glob, os.path, testoob, unittest


for moduleFilename in glob.glob('*Tests.py'):
   moduleName, _ = os.path.splitext(moduleFilename)
   module = __import__(moduleName)

   for moduleAttrName in dir(module):
      if moduleAttrName.endswith('Tests'):
         globals()[moduleAttrName] = getattr(module, moduleAttrName)


# Start program
if __name__ == "__main__":
   testoob.main()
