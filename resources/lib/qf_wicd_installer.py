#!/usr/bin/python

#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

#	Author Jonas Vikstrom (VIKJON0)

import os
import sys


def install_wicd (user, aPassword):
		generate_seed(user)

		sudo_command = "apt-get update"
		p = os.system('echo %s|sudo -S %s' % (aPassword, sudo_command))

		sudo_command = "apt-get install -y debconf-utils"
		p = os.system('echo %s|sudo -S %s' % (aPassword, sudo_command))

		sudo_command = "debconf-set-selections " + os.getcwd() + "/wcid-daemon.seed"

		p = os.system('echo %s|sudo -S %s' % (aPassword, sudo_command))

		sudo_command = "apt-get install -y wicd-curses"
		p = os.system('echo %s|sudo -S %s' % (aPassword, sudo_command))

		sudo_command = "sudo /etc/init.d/wicd start"
		p = os.system('echo %s|sudo -S %s' % (aPassword, sudo_command))

def check_installed():
		print "Checking if installed"
		from popen2 import Popen3		
	
		(stdin, stdout, stderr) = os.popen3("dpkg -l")#, mode, bufsize)
		s = stdout.read()
		
		if s.find("wicd-curses") == -1:
			return False
		else:
			return True
def generate_seed(user):
	#user = os.getlogin() 
	#user = os.getenv('USERNAME')
	#user = os.os.geteuid()
	line1 = "wicd-daemon	wicd/users	multiselect	" + user

	f=open(os.getcwd() + '/wcid-daemon.seed', 'w')
	f.write(line1)

if __name__ == '__main__':
	import getpass

	print "0 Quit"
	print "1 check if installed"
	print "2 Install wicd"
	aSelect = raw_input('Please enter a value:')

	if aSelect == "1":
		if check_installed() == True:
			print "wicd-cli is installed"
		else:
			print "wicd-cli is not installed"	
	elif aSelect == "2":
		aPassword = getpass.getpass("Pls type your password: ")
		install_wicd (aPassword)









