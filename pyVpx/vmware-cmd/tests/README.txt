vmware-cmd (Python version) tests

This directory has unit tests and infrastructure to
support them, some of which could be generally useful to any Python code, including:

 * A simple Mock object class.
   It logs and counts method calls so that tests can check that the SUT is
   invoking the mock in the expected way. E.g.:

    door = Door()
    door.Open()
    door.Close()
    door.Open()

    self.failIf(door.Open.callCount != 2)
    self.failIf(door.Close.callCount != 1)

 * A RawInputStub class that wraps the raw_input function and instead of
   prompting the user, returns a desired value. E.g.:

   >>> rawInputStub = RawInputStub()
   >>> rawInputStub.answer = 'foobar'
   >>> value = raw_input('Enter a word')
   Enter a word
   >>> value
   'foobar'

 * A FileWriteCapture class that can intercept file writes and then be
   queried for its contents.  This is very useful for capturing and verifying
   that output to sys.stdout and sys.stderr matches expectations. E.g.:

   >>> sys.stderr = FileWriteCapture(sys.stderr).StartCapture()
   >>> print >>sys.stderr, 'print',
   >>> sys.stderr.write(',write')
   >>> sys.stderr.getvalue()
   'print,write'

 * A TableDrivenTestCase class that can be subclassed and used to
   dynamically create test cases from a simple text file.

   Example 1 - PowerOpsTestsTable.txt:

   operation  powerOpMode  startState  toolsInstalled  newState  raisesFault  callCounts

   #    op     mode  oldState   t  newState   res  callCounts
   #------  -------  ---------  -  --------   ---  ------------

   Suspend     'xx'  off        0  off        IPM  {}

   Suspend     None  off        0  off        IPS  {'StandbyGuest':1,'Suspend':0}
   Suspend     None  off        1  off        IPS  {'StandbyGuest':1,'Suspend':0}
   Suspend     None  on         0  on         TU   {'StandbyGuest':1,'Suspend':0}
   Suspend     None  on         1  suspended  OK   {'StandbyGuest':1,'Suspend':0}

   Example 2 - EndToEndTestsTable.txt:

   argsStr                               expRc  expOut  expErr
   #--------                             -----  ------  ------

   unknown_server_op                         0  ''                       Invalid operation
   $vm unknown_vm_op                         0  ''                       Invalid operation
   $vm answer                                0  ''                       No questions pending.
   unknown_vm getstate                       0  ''                       No virtual machine found with name

   listdatastores                            0  '/vmfs/volumes'
   listvms                                   0  '$vm/$vm.vmx'
   -l                                        0  '$vm/$vm.vmx'


-- mabramow@vmware.com (2008-06-27)
