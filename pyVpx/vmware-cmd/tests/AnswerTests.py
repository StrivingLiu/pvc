#!/usr/bin/env python

"""
Test the "answer" vm operation.

"answer" is an interactive operation that prompts the user via the
Python built-in function `raw_input`, so we have do some clever things
with `RawInputStub` to override raw_input so that we can seed it with a
value and not actually prompt the user.

We also test that the operation behaves in a reasonable way when the
vm has no question pending or if the operation is invoked with an
unknown vm name.
"""

import sys
sys.path.append('../operations')
sys.path.append('./stubs')
sys.path.append('..')

import unittest, testoob
from HostStub import Host, pyVmomi
from VmStub import Vm
from Struct import Struct
from TestUtils import RawInputStub, FileWriteCapture
from Answer import Answer


class AnswerTests(unittest.TestCase):

   def setUp(self):
      """
      The fixture consists of a Host (stub) and a few instances ov Vm
      (Stub).
      """

      self.vmNoQuestion = Vm(name='noQuestion',
                             runtime=Struct(question=None))
      self.vmQuestion = Vm(name='Question',
                           runtime=Struct(
                              question=Struct(
                                 id='someQuestionId',
                                 text="What's up, doc?",
                                 choice=Struct(
                                    choiceInfo=[
                                       Struct(key='0', label='The sky'),
                                    ],
                                    defaultIndex=0,
                                 )
                              )
                           )
                        )
      self.host = Host('Fake host', [self.vmNoQuestion, self.vmQuestion])

      ## Replace `raw_input` with a version that we can automate.
      self.rawInputStub = RawInputStub()

   def tearDown(self):
      """
      Restore the original version of `raw_input`.
      """

      self.rawInputStub.destroy()

   def test_answer_noQuestion(self):
      """
      When the `answer` operation is invoked on a vm with no question
      pending, then we simply print an error message on stderr.
      """

      try:
         ## Capture what the SUT is writing to stderr so that we can
         ## verify it later.
         sys.stderr = FileWriteCapture(sys.stderr).StartCapture()

         result = Answer().DoIt(self.host, self.vmNoQuestion.name)

         expectOnStderr = 'No questions pending.\n'
         self.assertEqual(sys.stderr.getvalue(), expectOnStderr,
                          'Did not see "%s" on stderr'
                          % expectOnStderr.replace('\n', '\\n'))
         self.assertTrue(result is None,
                         'result == "%s"; result != None' % result)
      finally:
         ## Revert to the normal sys.stderr
         sys.stderr = sys.stderr.EndCapture()


   def test_answer_Question(self):
      try:
         ## Make rawInputStub act as if the user entered '0' in
         ## response to the question.
         self.rawInputStub.answer = '0'

         def _Answer(questionId, choice):
            """
            This function is a replacement for the Vm.Answer method
            that does nothing except check that it has been called
            with expected args.
            """

            self.assertEqual(questionId, self.vmQuestion.runtime.question.id,
                             '_Answer got questionId == "%s"' % questionId +
                             '; expected "%s"'
                             % self.vmQuestion.runtime.question.id)
            self.assertEqual(choice, self.rawInputStub.answer,
                             '_Answer got choice == "%s"' % choice +
                             '; expected "%s"' % self.rawInputStub.answer)

         ## Redefine the Answer method of the Vm stub so that it
         ## invokes our _Answer function.
         self.vmQuestion.Answer = _Answer

         ## Capture what the SUT is writing to stdout so that we can
         ## verify it later.
         sys.stdout = FileWriteCapture(sys.stderr).StartCapture()

         result = Answer().DoIt(self.host, self.vmQuestion.name)

         self.assertTrue(result is None,
                     'result == "%s"; result != None' % result)
      finally:
         ## Instead of checking what was written to sys.stdout
         ## verbatim (probably brittle), we check that various strings
         ## were all written to sys.stdout
         for aStr in ('Question (id = someQuestionId)',
                      self.vmQuestion.runtime.question.text,
                      'Select choice. Press enter for default',
                      'selected %s' % self.rawInputStub.answer):
            self.assertTrue(aStr in sys.stdout.getvalue(),
                            'Did not find "%s" in stdout' % aStr)

         ## Revert to the normal sys.stdout
         sys.stdout = sys.stdout.EndCapture()


   def test_answer_unknownVm(self):
      """
      Verify that we raise an appropriate exception if the operation
      is invoked with an unknown vm name.
      """

      self.failUnlessRaises(pyVmomi.vim.fault.NotFound,
                            Answer().DoIt, self.host, 'unknownVm')


# Start program
if __name__ == "__main__":
   testoob.main()
