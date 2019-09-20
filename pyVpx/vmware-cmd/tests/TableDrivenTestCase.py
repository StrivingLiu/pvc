import re, string, sys, unittest


class TableDrivenTestCase(unittest.TestCase):
   """
   To use this class:

   1) Subclass from it and in the new class...

   2) Override the value of the `testTableInputFile` class attribute
      to a file object with the test case data table.

      In the file:
       * Fields are separated by 2 or more spaces.
       * Lines beginning with '#' are comments.
       * The first non-comment, non-blank line is the list of field names.
         Remaining rows are data for test cases.
       * Field values are any Python expression valid in the
         subclass's module's namespace.

      Example file snippet below:

      operation  powerOpMode  startState  toolsInstalled  newState  raisesFault  callCounts

      #    op  mode  oldState   newState   res  callCounts
      #------  ----  ---------  --------   ---  ------------

      Suspend  soft  off        off        IPS  {'StandbyGuest':1,'Suspend':0}
      Suspend  soft  on         suspended  OK   {'StandbyGuest':1,'Suspend':0}
      Suspend  soft  suspended  suspended  IPS  {'StandbyGuest':1,'Suspend':0}

   3) Override the createTest classmethod. It should take a keyword
      param for each field in the data file.
   """

   table = None

   @classmethod
   def createTest(cls, **kwargs):
      """
      Subclass should override this.

      The function should take keyword args; one arg for each field in
      the table. It should return a test description (str) and a test
      method. As with typical unittest.TestCase methods, the method
      should take only a `self` param and should verify behavior with
      assert*, fail*, etc. methods. No return value is necessary or
      useful.
      """

      raise NotImplementedError  # Subclass: override me

   @classmethod
   def createTests(cls):
      """
      Iterates through the table of test cases in the file
      cls.testTableInputFile

      The first row is interpreted as the field names.

      The rest of the rows are interpreted as test case data and the
      method calls the createTest class method, passing it keyword
      args for all of the fields in each row.
      """

      inputFile = cls.testTableInputFile

      # Don't execute if there's no data to process
      if not inputFile: return

      testNum = 0

      re2Spaces = re.compile('\ {2,}')

      for lineNum, line in enumerate(inputFile):
         if line.startswith('#'): continue     # Ignore comments
         line = line[:-1].strip()              # Strip newline/spaces
         rowTuple = re.split(re2Spaces, line)  # Split on 2 or more spaces
         if len(rowTuple) <= 1: continue       # Ignore blank lines

         if testNum == 0:
            tableColumns = rowTuple
         else:
            rowDict = dict(zip(tableColumns, rowTuple))
            testName = 'test_%03d' % testNum
            testDesc, testMethod = cls.createTest(**rowDict)
            setattr(testMethod, '__doc__',
                    '%s.%s %s' % (cls.__name__, testName, testDesc))
            setattr(testMethod, '__name__', testName)
            setattr(cls, testName, testMethod)

         testNum += 1

   def failUnlessMockCallCountsEqual(self, mock, callCounts):
      """
      Checks that `mock` methods were called the # of times specified
      in callCounts.

      @param callCounts: Dict with method names and the number of
      times they're expected to be called.
      @type  callCounts: dict(str -> int)
      """

      for methodName, expectedCallCount in callCounts.items():
         actualCallCount = getattr(mock, methodName).callCount
         self.failIf(actualCallCount != expectedCallCount,
                     'Calls to mock method "%s": %d; expected: %d'
                     % (methodName, actualCallCount, expectedCallCount))
