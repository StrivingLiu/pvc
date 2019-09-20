import sys
from Operation import Operation


class Answer(Operation):

   usage = ''

   def DoIt(self, host, vm):
      vm = Operation.GetVm(host, vm)

      question = vm.runtime.question
      if not question:
         sys.stderr.write("No questions pending.\n")
         return None

      print('\nQuestion (id = %s) :%s' % (question.id, question.text))

      choices = {}
      for choice in question.choice.choiceInfo:
         choices[choice.key] = choice.label
         print('\t%s) %s' % (choice.key, choice.label))

      choice = raw_input('Select choice. Press enter for default <%s> : '
                         % question.choice.defaultIndex)
      if choice:
         print('selected %s : %s' % (choice, choices[choice]))
      else:
         choice = str(question.choice.defaultIndex)

      ret = vm.Answer(question.id, choice)
