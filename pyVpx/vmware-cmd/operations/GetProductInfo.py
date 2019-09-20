from Operation import Operation


class GetProductInfo(Operation):

   usage = '<product_info>'

   def DoIt(self, host, vm, productInfo):
      if productInfo == 'product':
         return host.about.productLineId
      elif productInfo == 'platform':
         return host.about.osType
      elif productInfo == 'build':
         return host.about.build
      elif productInfo == 'majorversion':
         return host.about.version.split('.')[0]
      elif productInfo == 'minorversion':
         return host.about.version.split('.')[1]
      elif productInfo == 'revision':
         return host.about.version.split('.')[2]
