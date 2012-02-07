#!/usr/bin/python
# coding=euc-kr
#
# TelnetAuto.py
#
# Ref ; http://harookie.springnote.com/pages/769022

from telnetlib import Telnet
import time, sys
import getopt
from threading import *

from CommandList import AutoLogin
from CommandList import Command
from CommandList import CommandList

host = '192.168.10.1'
port = 23
userid='userid'
passwd='passwd'

class ReaderThread(Thread):
	def __init__(self, telnet, filename):
		self.telnet = telnet
		Thread.__init__(self)
		self.str = ''
		self.count = 0
		self.autoLogin = AutoLogin(userid, passwd)
		self.login_success = 0
		self.commandList = CommandList()
		self.commandList.ReadFile(filename)
		
	def check_login(self, str) :
		ret = self.autoLogin.Check(str)
		if ret == True :
			self.login_success = 1
		elif ret == False :
			print "Login Failed..........\n"
			return 1
		elif ret == None :
			pass
		else :
			self.telnet.write(ret+'\n')
		return 0
		
	def run_command(self, str) :
		# 1번째 명령어에 대한 응답을 확인한다.
		ret = self.commandList.Check(str)
		if ret == True :
			# 명령어 결과 확인
			#self.telnet.write('\n')
			ret = 1
		elif ret == False :
			# 모든 명령어 확인 완료
			ret = 0
		elif ret == None :
			# 아직 명령어 결과를 확인하지 못함
			ret = 0
		else :
			# 수행해야 할 명령어
			self.telnet.write(ret + '\n')
			ret = 0
			
		return ret
		
	def run(self):
		while 1:
			str = self.telnet.read_some()
			self.str += str	# read_some 으로 읽어오는 경우는 데이터가 짤려서 올라오므로, 이를 self.str 에 저장해서 비교한다.
			if str == '': break
			if self.login_success == 0 :
				str1 = ""
				# 서버에서 문장이 연결되어서 오는 경우가 있어서 \n 으로 나눠서 처리
				for str1 in self.str.split('\n') :
					ret = self.check_login(str1)
					if ret == 1 :	# 로그인 실패이므로 접속 종료
						return
				self.str = ''	# 모두 확인했으므로 이젠 지운다
			else :
				# login_success
				#print '====str[%s][%d]====\n' % (self.str, len(self.str))
				while 1 :
					ret = self.run_command(self.str)
					if ret == 1 :
						# 원하는 결과 문장을 찾았다. 다음 명령어 수행
						self.str = ""
					else :
						# 원하는 문장을 찾지 못했으므로 Carriage Return 까지는 완성된 문장으로 보고 완성된 문장을 지운다
						pos = self.str.rfind('\r\n')
						if pos >= 0 :
							self.str = self.str[pos:]
						break
			
			sys.stdout.write(str)
			sys.stdout.flush()
			
def main(host, port, filename):
	telnet = Telnet()
	telnet.open(host, port)
	reader = ReaderThread(telnet, filename)
	reader.start()
	while 1:
		if not reader.isAlive(): break
		try: 
			line = raw_input()
		except EOFError as exc:
			# If KeyboardInterrupt is not raised in 50ms, it's a real EOF event.
			telnet.write('\003\n')
			raise
		if line.find('break') >= 0 :
			# 서버로 Ctrl-C 를 보내어서 현재 진행 중인 작업을 중지시킨다.
			telnet.write('\003\n')
		else :
			telnet.write(line+'\n')
		time.sleep(0.3)
	telnet.close()
	
if __name__ == '__main__':
	version = '1.0'
	basename = 'TelnetAuto.py'
	filename = ''
	usage = """
Version : %s
Usage: %s -l hostip [-o port] -u username -p password -c command_filename
    -l  host ip address
    -o  host port number
    -u  host login id
    -p  host login pw
    -c  command filename
    -h  print this usage
Example:  %s -l %s -o %d -u %s -p %s -c %s
""" % (version, basename, basename, host, port, userid, passwd, filename)
	
	optlist, arglist = getopt.getopt(sys.argv[1:], 'hl:o:u:p:c:')
	cmd_list = [ ]
	for o, a in optlist:
		if o == '-h':
			print usage
			sys.exit(0)
		elif o == '-l':
			host = a
		elif o == '-o':
			port = int(a)
		elif o == '-u':
			userid = a
		elif o == '-p':
			passwd = a
		elif o == '-c':
			filename = a
		else:
			print usage
			sys.exit(1)
	#print "info: %s %d %s %s %s %d" % (ip, port, userid, passwd, cmd, timeout)
	
	if (len(host)==0 or len(userid)==0 or len(passwd)==0) :
		print usage
		sys.exit(1)
	
	main(host, port, filename)
