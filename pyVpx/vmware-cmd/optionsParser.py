import sys, operations, optparse
from Formatter import Formatter
from formatters import *


class MyOptionParser(optparse.OptionParser):

   def print_help(self):
      """
      Override and extend OptionParser.print_help so that it displays separate sections for server operations and vm operations.
      """

      optparse.OptionParser.print_help(self)
      print(self.GetUsageMessage(operations.serverOpClasses,
                                 operations.vmOpClasses))

   def GetUsageMessage(self, serverOpClasses, vmOpClasses):
      """
      Display usage message for the app.
      """

      def GetUsageForOps(opClasses, formatStr):
         lines = []

         for opClass in opClasses:
            if hasattr(opClass, 'hidden'): continue
            args = opClass.GetArgSpec()
            usageString = formatStr % (
               sys.argv[0], opClass.GetName(), opClass.usage or args)
            lines.append('    %-75s %s' % (usageString, opClass.notes))

         return '\n'.join(lines)

      return '''
  Server Operations:
%(dashLUsage)s
%(serverOpsUsage)s

  VM Operations:
%(vmOpsUsage)s''' % dict(
         dashLUsage      = '    %s -l' % sys.argv[0],
         serverOpsUsage  = GetUsageForOps(serverOpClasses, '%s -s %s %s'),
         vmOpsUsage      = GetUsageForOps(vmOpClasses, '%s <cfg> %s %s'))


parser = MyOptionParser()

# Allow us to have operation-specific options.
# With this true:
#   vmware-cmd listdevices --tree
# would get interpreted as:
#   vmware-cmd --tree listdevices
# and optparse would flag the unknown option "--tree"
# With it false, the above command would be interpreted as:
#   vmware-cmd listdevices -- --tree
# and "--tree" would be an arg that we could later pass
# to a command-specific OptionParser.
parser.allow_interspersed_args = False

parser.add_option("-v",
                  action="store_true", dest="verbose",
                  help="Verbose.")
parser.add_option("-q",
                  action="store_true", dest="quiet",
                  help="Quiet. Minimal output.")
parser.add_option("--interactive", "-i",
                  action="store_true",
                  help=optparse.SUPPRESS_HELP)
                  #help="Launch interactive command shell")
parser.add_option("--test",
                  action="store_true",
                  help=optparse.SUPPRESS_HELP)
                  #help="Test mode")
parser.add_option("-l",
                  action="store_const", const="listvms", dest="serverOp",
                  help=optparse.SUPPRESS_HELP)
parser.add_option("-s",
                  dest="serverOp",
                  help=optparse.SUPPRESS_HELP)

connectionOptGroup = optparse.OptionGroup(parser, 'Connection Options')
connectionOptGroup.add_option("-H",
                              dest="hostname",
                              default="localhost",
                              metavar="<host>",
                              help="specifies an alternative host " +
                                   "(if set, -U and -P must also be set)")
connectionOptGroup.add_option("-O",
                              dest="port",
                              metavar="<port>",
                              default=443,
                              help="specifies an alternative port")
connectionOptGroup.add_option("-U",
                              dest="user",
                              metavar="<username>",
                              default="root",
                              help="specifies a user")
connectionOptGroup.add_option("-P",
                              dest="password",
                              metavar="<password>",
                              help="specifies a password")
connectionOptGroup.add_option("-N",
                              dest="namespace",
                              metavar="<namespace>",
                              default="vim25/5.5", # Works for ESX 4 hosts
                              help=optparse.SUPPRESS_HELP)
                              #help="specifies the SOAP namespace")
parser.add_option_group(connectionOptGroup)

outputFormatOptGroup = optparse.OptionGroup(parser, 'Output Format Options')
outputFormatOptGroup.add_option(
   "--format",
   action="store", dest="format", metavar="FORMAT",
   type="choice", choices=['simple', 'html', 'xml', 'json', 'tree'],
   default='simple',
   help=optparse.SUPPRESS_HELP)
   #help="Output format (simple, html, xml, json)")
outputFormatOptGroup.add_option(
   "--attributes",
   dest="attrs", metavar="ATTRIBUTES",
   help=optparse.SUPPRESS_HELP)
   #help="Attributes to output")
outputFormatOptGroup.add_option(
   "--sort-by-attributes",
   dest="sortByAttrs", metavar="ATTRIBUTES",
   help=optparse.SUPPRESS_HELP)
   #help="Fields by which to sort tabular data display")
outputFormatOptGroup.add_option(
   "--group-by-attributes",
   dest="groupByAttrs", metavar="ATTRIBUTES",
   help=optparse.SUPPRESS_HELP)
   #help="Valid for --format=tree only; fields by which to " +
   #     "collect items under a common node")
#parser.add_option_group(outputFormatOptGroup)


def GetOutputFormatOptionsDict(options):
   resultDict = {}

   for attr in ('groupByAttrs', 'sortByAttrs', 'attrs'):
      attrValue = getattr(options, attr)
      if attrValue:
         resultDict[attr] = attrValue.split(',')

   return resultDict


def GetFormatter(options):
   return Formatter.GetByType(
      options.format,
      kwargs=GetOutputFormatOptionsDict(options))


def GetConnectSpec(options):
   return options.hostname, options.user, options.password, options.namespace
