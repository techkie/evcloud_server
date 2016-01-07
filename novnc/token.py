#coding=utf-8

########################################################################
#@author:   bobfu
#@email:    fubo@cnic.cn
#@date:     2015-10-19
#@desc:    novnc token管理模块。完成读写novnc的token配置文件，使用单例模式
#			防止并发写文件操作导致数据不同步。			
########################################################################

import os, uuid
import commands
from compute.models import Vm
from compute.vm.vm import VM, VIR_DOMAIN_RUNNING
from django.conf import settings

import thread

class TokenManager(object):
	class TManager(object):
		novnc_tokens = {}
		lock = thread.allocate_lock()
		def __init__(self):
			path = os.path.dirname(os.path.abspath(__file__))
			self._token_file_path = path+'/novnc/vnc_tokens'
			tokens_file = open(self._token_file_path, 'r')
			for token in tokens_file.readlines():
				t = token.strip().split(':', 1)
				if len(t)<2:
					continue
				self.novnc_tokens[str(t[1].strip())] = str(t[0].strip())
			tokens_file.close()

		def add_token(self, vncid, hostip, port):
			self.lock.acquire()
			self.novnc_tokens['%s:%d' % (hostip, port)] = str(vncid)
			self.flush()
			self.lock.release()

		def del_token(self, vncid):
			self.lock.acquire()
			for k, v in self.novnc_tokens.items():
				if v == vncid:
					del self.novnc_tokens[k]
			# print self.novnc_tokens
			self.flush()
			self.lock.release()

		def flush(self):
			tokens_file = open(self._token_file_path, 'w')
			for k, v in self.novnc_tokens.items():
				tokens_file.write('%s: %s\n' % (v, k))
			tokens_file.close()

	instance = TManager()


