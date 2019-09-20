from Utils import rec_getattr


class FormatOptions(object):
   """
   Holds a list of ordered column names (i.e.: fields of a record
   to display) and dicts to hold options related to the columns.
   """

   def __init__(self):
      self.Clear()

   def Clear(self):
      self.columns = []
      self.columnOptions = {}

   def AddColumn(self, column, **columnOptions):
      self.columns.append(column)
      self.columnOptions[column] = dict(columnOptions)

   def SetColumns(self, columns):
      self.Clear()
      
      for column in columns:
         self.AddColumn(column, maxWidth=0)

   def GetColumnsInfo(self):
      return [ (column, self.columnOptions[column])
               for column in self.columns ]
   
   classOptions = {}
   """
   dict of string(name of record object class) -> FormatOptions
   
   Given a type of record object we want to display, we can determine
   what columns to show and get options (e.g.: maxWidth) that
   influence how we format them.
   """

   @classmethod
   def GetByName(cls, name):
      formatOptions = cls.classOptions.get(name)
      if not formatOptions:
         cls.classOptions[name] = FormatOptions()
         formatOptions = cls.classOptions[name]

      return formatOptions


FormatOptions.GetByName('Vm').SetColumns(['localPath'])
FormatOptions.GetByName('Device').SetColumns(
   ['deviceInfo.label',
    'idString',
    'connectable.connected',
    ])
FormatOptions.GetByName('vim.Datastore').SetColumns(
   ['info.name',
    'info.url',
    'info.freeSpace',
    ])
FormatOptions.GetByName('vim.Task').SetColumns(
   ['info.descriptionId',
    'info.entityName',
    'info.state',
    'info.error.message',
    'info.completeTime',
    ])

   
class Formatter(object):
   """
   A base class for object that know how to format data, including
   tabular data. To create a new formatter, subclass this class
   and override the following method:
   
      def FormatField(self, key, value, width):
         return ''
   """

   idToClass = {}
   """
   dict of string -> subclass of Formatter
   
   Allows us to register and get specific formatter subclasses
   using a string name (e.g.: "simple" or "xml").
   """
   
   @classmethod
   def Register(cls, formatterClass):
      cls.idToClass[formatterClass.__name__.lower()] = formatterClass
      
   @classmethod
   def GetByType(cls, formatType, kwargs={}):
      return cls.idToClass[formatType + 'formatter'](**kwargs)

   def __init__(self,
                attrs=None,
                sortByAttrs=None,
                dataStart='',
                listStart='',
                listEnd='',
                listItemStart='',
                fieldSep='',
                listItemSep='',
                listItemEnd='',
                dataEnd=''):
      """
      Initialize a formatter

      Subclasses must call this and they can customize the parameters
      to get different kinds of formatting.
      """

      self.attrs = attrs
      self.sortByAttrs = sortByAttrs
      self.dataStart = dataStart
      self.listStart = listStart
      self.listEnd = listEnd
      self.listItemStart = listItemStart
      self.fieldSep = fieldSep
      self.listItemSep = listItemSep
      self.listItemEnd = listItemEnd
      self.dataEnd = dataEnd
      self.numRecords = 0

   def Format(self, data):   
      return self.dataStart + str(self._Format(data)) + self.dataEnd

   def _Format(self, data):
      if isinstance(data, list):
         return self.FormatList(data)
      elif isinstance(data, bool):
         return int(data)
      else:
         formatOptions = FormatOptions.GetByName(type(data).__name__)
         if formatOptions and len(formatOptions.columns) > 0:
            return self.FormatRecord(data)
         else:
            return data

   def FormatList(self, data):
      if len(data) <= 0: return ''

      formatOptions = FormatOptions.GetByName(data[0].__class__.__name__)
         
      if self.attrs: formatOptions.SetColumns(self.attrs)
      self.columnsInfo = formatOptions.GetColumnsInfo()
      self.columnsInfo = _CalcMaxWidthsForColumns(data, self.columnsInfo)

      if self.sortByAttrs: _SortList(data, self.sortByAttrs)

      return ('%s%s%s'
              % (self.listStart,
                 self.listItemSep.join(map(self.FormatListItem, data)),
                 self.listEnd))

   def FormatListItem(self, record):
      return ('%s%s%s'
              % (self.listItemStart, self._Format(record), self.listItemEnd))

   def FormatRecord(self, record):
      return self.fieldSep.join(
         [ self.FormatField(key=column,
                            value=rec_getattr(record, column),
                            width=columnOptions['maxWidth'])
           for column, columnOptions in self.columnsInfo ] ).rstrip()

   def FormatField(self, key, value, width):
      """
      Subclasses should define this function.
      """
      
      pass

def _CalcMaxWidthsForColumns(data, columnsInfo):
   for record in data:
      for column, columnOptions in columnsInfo:
         value = str(rec_getattr(record, column))
         columnOptions['maxWidth'] = max(columnOptions['maxWidth'], len(value))

   return columnsInfo


def _SortList(data, sortByAttrs):
   def _key(x): return getattr(x, sortByAttrs[0])
   def _cmp(x, y): return cmp(x._sortKey, y._sortKey)
   
   for item in data: item._sortKey = _key(item)
   
   data.sort(_cmp)


Register = Formatter.Register
