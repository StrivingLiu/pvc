import sys
import ssl
import json

import pyVim
import pyVim.connect
import pyVim.task

PORT=443

def PyVimConnect(host, user='Administrator@vsphere.local', pwd='Admin!23',
                 version='vim.version.version11'):
	context = None
	if sys.version_info >= (3, 0):
		context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
	elif getattr(ssl, '_create_unverified_context', None):
		ssl._create_default_https_context = ssl._create_unverified_context
	return pyVim.connect.Connect(host=host, user=user, pwd=pwd,
                               version=version, sslContext=context)

def QueryBuildUrl(url, server='buildapi.eng.vmware.com'):
	''' Connects to buildAPI server and queries the url'''
	if (sys.version_info[0] == 3):
		import http.client as httplib
	else:
		import httplib
	c = httplib.HTTPConnection(server, '80')
	c.debuglevel = 0
	c.request('GET', url)
	r = c.getresponse()
	try:
		if r.status == 200:
			out = json.loads(r.read().decode('utf-8'))
			return out
		else:
			raise Exception('Unable to query url %s: status %d' % (url, r.status))
	except Exception as e:
		raise e
	finally:
		c.close()


if __name__=="__main__":
	pass