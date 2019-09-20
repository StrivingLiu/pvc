#!/usr/bin/env python

"""
"""

import sys, unittest, testoob
from TestUtils import RawInputStub, FileWriteCapture

stderrName = sys.stderr.name
stderrClassName = sys.stderr.__class__.__name__
rawInputModule = raw_input.__module__


class FileWriteCaptureTests(unittest.TestCase):

   def test_start_and_end(self):
      try:
         self.failIf(sys.stderr.__class__.__name__ != stderrClassName,
                     'sys.stderr.__class__.__name__ was "%s"'
                     % sys.stderr.__class__.__name__ +
                     '; expected "%s"'
                     % stderrClassName)
         self.failIf(sys.stderr.name != stderrName)
         self.failIf(hasattr(sys.stderr, '_buf'))

         sys.stderr = FileWriteCapture(sys.stderr)

         # Before calling StartCapture - sys.stderr should be plain
         # ol' stderr.
         self.failIf(sys.stderr.name != stderrName)
         self.failIf(sys.stderr._buf.name != stderrName)

         sys.stderr.StartCapture()

         # After StartCapture, it should be a FileWriteCapture instance
         # and it's a `_buf` attribute should be a `StringO` or `StringIO`.
         self.failIf(sys.stderr.__class__.__name__ != 'FileWriteCapture')
         self.failIf(sys.stderr._buf.__class__.__name__
                     not in 'StringO', 'StringIO')
      finally:
         sys.stderr = sys.stderr.EndCapture()

         # After EndCapture, everything should be restored.
         self.failIf(sys.stderr.__class__.__name__ != stderrClassName)
         self.failIf(sys.stderr.name != stderrName)
         self.failIf(hasattr(sys.stderr, '_buf'))

   def test_print(self):
      try:
         sys.stderr = FileWriteCapture(sys.stderr).StartCapture()
         stringToPrint = 'We have to move the island.'
         print >>sys.stderr, stringToPrint,

         self.failIf(sys.stderr.getvalue() != stringToPrint,
                     'Saw "%s" on stderr; expected "%s"'
                     % (sys.stderr.getvalue(), stringToPrint))
      finally:
         sys.stderr = sys.stderr.EndCapture()

   def test_write(self):
      try:
         sys.stderr = FileWriteCapture(sys.stderr).StartCapture()
         stringToWrite = 'Destiny is a fickle bitch.'
         sys.stderr.write(stringToWrite)

         self.failIf(sys.stderr.getvalue() != stringToWrite,
                     'Saw "%s" on stderr; expected "%s"'
                     % (sys.stderr.getvalue(), stringToWrite))
      finally:
         sys.stderr = sys.stderr.EndCapture()


class RawInputStubTests(unittest.TestCase):

   def test_RawInputStub(self):
      try:
         sys.stdout = FileWriteCapture(sys.stdout).StartCapture()

         self.failIf(raw_input.__module__ != rawInputModule,
                     'raw_input.__module__ = "%s"; expected "%s"'
                     % (raw_input.__module__, rawInputModule))

         rawInputStub = RawInputStub()
         rawInputStub.answer = 'foobar'

         prompt = 'Enter a word'
         value = raw_input(prompt)

         self.failIf(sys.stdout.getvalue() != '%s\n' % prompt,
                     'Saw "%s" on stdout; expected "%s"'
                     % (sys.stdout.getvalue(), '%s\n' % prompt))
         self.failIf(value != rawInputStub.answer,
                     'raw_input returned "%s"; expected "%s"'
                     % (value, rawInputStub.answer))
      finally:
         self.failIf(raw_input.__module__ != 'TestUtils')
         rawInputStub.destroy()
         self.failIf(raw_input.__module__ != rawInputModule,
                     'raw_input not restored after rawInputStub.destroy()? ' +
                     'raw_input.__module__ = "%s"; expected "%s"'
                     % (raw_input.__module__, rawInputModule))

         sys.stdout = sys.stdout.EndCapture()



if __name__ == "__main__":
   testoob.main()
