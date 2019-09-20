#!/usr/bin/env python

"""
Python reimplementation of vmware-cmd tool.

This tool, written in Python, attempts to duplicate as much
functionality as possible from the classic Perl-based vmware-cmd tool,
and it adds a few tricks of its own, like more flexible and intuitive
command-line parsing, configurable output formats, and an interactive
shell mode (-i).

This tool currently relies on pyVim (and pyVmomi).
"""

import sys, optionsParser, SharedSocketFix
import CommandProcessor
from Shell import Shell
from Host import Host
from TaskManager import TaskManager
from Task import TaskBlocked


def GetHostStub(name):
   sys.path.insert(0, './tests')
   sys.path.insert(0, './tests/stubs')
   return __builtins__.__import__(name).GetHost()


def GetHost(options):
   if options.test:  return GetHostStub(options.hostname)
   else:             return Host.GetHost(optionsParser.GetConnectSpec(options))


def GetPrologue(operationName, args):
   if operationName in args:
      args = args[args.index(operationName) + 1:]

   return '%s(%s) = ' % (operationName, ', '.join(args))


def main(args=None):
   """
   Entry point for both command-line and shell

   Note that the `args` parameter to this function allows us to do
   stuff from the Python interactive prompt:

   >>> Main.main(['-H', 'pivot02', 'getstate', 'mabramow-test1'])
   getstate(mabramow-test1) = off

   Inspiration from http://www.artima.com/weblogs/viewpost.jsp?thread=4829
   """

   try:
      options, args = optionsParser.parser.parse_args(args or sys.argv[1:])
      if options.serverOp: args.insert(0, options.serverOp)

      host = GetHost(options)

      if options.interactive:
         Shell(host).cmdloop()
      else:
         operationName, result = CommandProcessor.Process(host, args)
         if result is not None:
            result = TaskManager().HandleIfTask(result, async=False)
                  
            if not options.quiet:
               if isinstance(result, basestring) or \
                  isinstance(result, int) or isinstance(result, long):
                  sys.stdout.write(GetPrologue(operationName, args))

            if result == 'success':  result = 1
            if result == 'error':    result = 0

            print(optionsParser.GetFormatter(options).Format(result))
   except CommandProcessor.InvalidOperation:
      sys.stderr.write('Invalid operation specified.\n\n')
      optionsParser.parser.print_help()
      sys.stderr.write('\nInvalid operation specified.\n')
   except CommandProcessor.InvalidParameter, e:
      sys.stderr.write('Invalid parameter specified.\n\n')
      sys.stderr.write('%s\n' % e)
   except TaskBlocked:
      sys.stderr.write('Virtual machine requires user input to continue\n')
   except KeyboardInterrupt:
      sys.stderr.write('\nKeyboardInterrupt\n')
   except AttributeError, e:
      sys.stderr.write('%s\n' % e)


# Start program
if __name__ == "__main__":
    main()
