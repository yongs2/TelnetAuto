#!/usr/bin/python
# coding=euc-kr
#
# CommandList.py
#

import unittest
import re

class AutoLogin :
	def __init__(self, userid, passwd) :
		self.userid = userid
		self.passwd = passwd
		self.state = 0
		self.nRetry = 0
		self.nMaxRetry = 3
		
	def SetMaxRetry(self, max_retry) :
		self.nMaxRetry = max_retry
		
	def Check(self, str) :
		if (self.state == 0) and str.find('login: ') >= 0 :
			# user id �Է� ���� Ȯ��
			self.state += 1		# ������ password �Է� ���� Ȯ��
			return self.userid
		elif (self.state == 1) and str.find('Password: ') >= 0 :
			# password �Է� ���� Ȯ��
			self.state += 1		# �Է� �Ϸ�
			return self.passwd
		elif (self.state == 2) and str.find('Login incorrect') >= 0 :
			# �α��� ����
			if(self.nRetry >= self.nMaxRetry) :
				return False
			self.state = 0
			self.nRetry += 1
			return None
		elif (self.state == 2) and str.find('Last login:') >= 0 :
			# �α��� ����
			return True
			
class Command :
	def __init__(self, command, wait_message):
		self.command = command
		self.wait_message = wait_message
		self.bInputCommand = False
		self.bDetectWaitMessage = False
		
class CommandList :
	def __init__(self):
		self.command = []
		self.index = 0
		
	def Check(self, str) :
		if (self.index >= len(self.command)) :
			# �� �̻� command�� �����Ƿ� Ȯ���� �ʿ䰡 ����.
			return False
			
		command = self.command[self.index]
		if command.bInputCommand == False :
			# ��ɾ� �Է��� ���� ��ɾ� ������ ����
			command.bInputCommand = True
			command.bDetectWaitMessage = False
			return command.command
		else :
			# ��ɾ� ����� ��
			if str.find(command.wait_message) >= 0 :
				self.bDetectWaitMessage = True
				self.index += 1
				return True		# ��ɾ� ����� ��ġ�����Ƿ� ���� �ڵ带 �����Ѵ�.
			else :
				return None		# ��ɾ� ����� ��ġ���� �ʾ����Ƿ� �׳� ���� ó���Ѵ�.
			
	def Add(self, command) :
		self.command.append(command)
		
	def Count(self) :
		return len(self.command)
		
	def GetCommand(self, index) :
		return self.command[index].command
		
	def GetWaitMessage(self, index) :
		return self.command[index].wait_message
		
	def ReadFile(self, filename) :
		nothandle = [ '#', '\r', '\n' ]
		# PATTERN ; 'command', 'message'
		pattern = re.compile(r" *\'([^,]*)\'\D*\'([^,]*)\'")
		
		if not filename :
			return
			
		f = open(filename, 'r')
		while 1: 
			line = f.readline()
			line.strip()
			if not line: break
			if line[0] in nothandle :
				pass
			else :
				# PATTERN ; 'command', 'message'
				m = pattern.search(line)
				if m :
					if m.group(1) and m.group(2) :
						print "    command=[%-10s], messasge=[%-10s]" % (m.group(1), m.group(2))
						self.Add(Command(m.group(1), m.group(2)))
		f.close()
		
class AutoLoginTest(unittest.TestCase):
	def testSuccess(self):
		autoLogin = AutoLogin('userid', 'passwd')
		
		# ����� ID �Է�
		self.assertEquals(None, autoLogin.Check('CentOS release 5.7 (Final)'))
		self.assertEquals('userid', autoLogin.Check('login: '))
		self.assertEquals('passwd', autoLogin.Check('Password: '))
		self.assertEquals(True, autoLogin.Check('Last login: Mon Jan  9 11:07:12 from 10.1.1.37'))
		
	def testFail(self):
		autoLogin = AutoLogin('userid', 'passwd')
		
		# ����� ID �Է�
		self.assertEquals(None, autoLogin.Check('CentOS release 5.7 (Final)'))
		self.assertEquals('userid', autoLogin.Check('login: '))
		self.assertEquals('passwd', autoLogin.Check('Password: '))
		self.assertEquals(None, autoLogin.Check('Login incorrect'))
		self.assertEquals('userid', autoLogin.Check('login: '))
		self.assertEquals('passwd', autoLogin.Check('Password: '))
		self.assertEquals(None, autoLogin.Check('Login incorrect'))
		self.assertEquals('userid', autoLogin.Check('login: '))
		self.assertEquals('passwd', autoLogin.Check('Password: '))
		self.assertEquals(None, autoLogin.Check('Login incorrect'))
		self.assertEquals('userid', autoLogin.Check('login: '))
		self.assertEquals('passwd', autoLogin.Check('Password: '))
		self.assertEquals(False, autoLogin.Check('Login incorrect'))
		
class CommandListTest(unittest.TestCase):
	def test1(self):
		prompt = 'localhost ~]'
		prompt2 = '@localhost tmp]'
		commandList = CommandList()
		commandList.Add(Command('mkdir tmp', 						'~]$'))
		commandList.Add(Command('cd tmp', 							'@localhost tmp]'))
		commandList.Add(Command('wget http://cdnetworks-kr-2.dl.sourceforge.net/project/netpbm/super_stable/10.35.83/netpbm-10.35.83.tgz netpbm-10.35.83.tgz',	' saved' ))
		commandList.Add(Command('tar -zxvf netpbm-10.35.83.tgz',	'@localhost tmp]'))
		commandList.Add(Command('cd netpbm-10.35.83',				'@localhost tmp]'))
		commandList.Add(Command('./configure',						'Hit ENTER to begin'))
		commandList.Add(Command('',								'Platform [gnu]'))
		commandList.Add(Command('',								'regular or merge [regular]'))
		commandList.Add(Command('',								'static or shared [shared]'))
		commandList.Add(Command('',								'(y)es or (n)o [y]'))
		commandList.Add(Command('',								'[<inttypes.h>] ==>'))
		commandList.Add(Command('',								'[libjpeg.so] ==>'))
		commandList.Add(Command('',								'JPEG header directory [default]'))
		commandList.Add(Command('',								'[libtiff.so] ==>'))
		commandList.Add(Command('',								'TIFF header directory [default]'))
		commandList.Add(Command('',								'[libz.so] ==>'))
		commandList.Add(Command('',								'Z header directory [default]'))
		commandList.Add(Command('',								'[libX11.so] ==>'))
		commandList.Add(Command('',								'X11 header directory [default]'))
		commandList.Add(Command('',								'[none] ==>'))
		commandList.Add(Command('',								'[http://netpbm.sourceforge.net/doc/] ==>'))
		#commandList.Add(Command('',								"Now you may proceed with 'make'"))
		commandList.Add(Command('ls -a',							'@localhost netpbm-10.35.83]'))
		commandList.Add(Command('ls -la',							'@localhost netpbm-10.35.83]'))
		self.assertEquals(23, commandList.Count())
		
		# 1��° ��ɾ� �Է�
		self.assertEquals('mkdir tmp', commandList.Check('Last login:'))
		self.assertEquals(True, commandList.Check('~]$'))
		
		# 2��° ��ɾ� �Է�
		self.assertEquals('cd tmp', commandList.Check(prompt))
		self.assertEquals(True, commandList.Check(prompt2))
		
		# 3��° ��ɾ� �Է�
		self.assertEquals('wget http://cdnetworks-kr-2.dl.sourceforge.net/project/netpbm/super_stable/10.35.83/netpbm-10.35.83.tgz netpbm-10.35.83.tgz', commandList.Check(prompt))
		self.assertEquals(True, commandList.Check(' saved'))
		
		# 4��° ��ɾ� �Է�
		self.assertEquals('tar -zxvf netpbm-10.35.83.tgz', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check(prompt2))
		
		# 5��° ��ɾ� �Է�
		self.assertEquals('cd netpbm-10.35.83', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check(prompt2))
		
		# 6��° ��ɾ� �Է�
		self.assertEquals('./configure', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('Hit ENTER to begin'))
		
		# 7��° ��ɾ� �Է�
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('Platform [gnu]'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('regular or merge [regular]'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('static or shared [shared]'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('(y)es or (n)o [y]'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('[<inttypes.h>] ==>'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('[libjpeg.so] ==>'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('JPEG header directory [default]'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('[libtiff.so] ==>'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('TIFF header directory [default]'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('[libz.so] ==>'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('Z header directory [default]'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('[libX11.so] ==>'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('X11 header directory [default]'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('[none] ==>'))
		
		self.assertEquals('', commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('[http://netpbm.sourceforge.net/doc/] ==>'))
		
		#self.assertEquals('',commandList.Check(prompt2))
		#self.assertEquals(True, commandList.Check("Now you may proceed with 'make'"))
		
		self.assertEquals('ls -a',commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('@localhost netpbm-10.35.83]'))
		
		self.assertEquals('ls -la',commandList.Check(prompt2))
		self.assertEquals(True, commandList.Check('@localhost netpbm-10.35.83]'))
	

if __name__ == "__main__":
    unittest.main()
