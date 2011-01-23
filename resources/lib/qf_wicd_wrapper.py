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
#	Based on wicd-cli & wicd-curses

# properties used in wicd
#afterscript = None
#dhcphostname = XBMCLive
#bssid = 00:26:5A:D0:10:B0
#postdisconnectscript = None
#dns_domain = None
#quality = 55
#gateway = None
#use_global_dns = False
#strength = -71
#encryption = True
#bitrates = 6 Mb/s
#ip = None
#beforescript = None
#hidden = False
#channel = 12
#mode = Master
#has_profile = True
#netmask = None
#key = mykey
#usedhcphostname = 0
#predisconnectscript = None
#enctype = wpa
#dns3 = None
#dns2 = None
#search_domain = None
#use_settings_globally = True
#use_static_dns = False
#encryption_method = WPA2
#essid = 1969c
#automatic = 1
#dns1 = None


#TODO: Add wired functionality
#TODO: enctype translation is not good enough? Or can method be used?
#TODO: Clean up error handling and possibly re-write as class.
#TODO: support for static ip etc

import os
import sys
import dbus
import dbus.service
import socket

from wicd import misc


if getattr(dbus, 'version', (0, 0, 0)) < (0, 80, 0):
	import dbus.glib
else:
	from dbus.mainloop.glib import DBusGMainLoop
	DBusGMainLoop(set_as_default=True)

################################################################################
#Basic wicd functions
###################################################################
def init():
	bus = dbus.SystemBus()

	misc.RenameProcess('qf-wicd-wrapper')

	try:
		daemon = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon'),
			'org.wicd.daemon')
		wireless = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wireless'),
			'org.wicd.daemon.wireless')
		wired = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wired'),
			'org.wicd.daemon.wired')
		config = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/config'),
			'org.wicd.daemon.config')
		return daemon, wireless, wired, config	
	except dbus.DBusException:
		print 'Error: Could not connect to the daemon. Please make sure it is running.'
		print '(sudo /etc/init.d/wicd start)'
		sys.exit(3)


def is_valid_wireless_network_id(network_id):
	if not (network_id >= 0 \
			and network_id < wireless.GetNumberOfNetworks()):
		print 'Invalid wireless network identifier.'
		return False
	else:
		return True

def is_valid_wired_network_id(network_id):
	num = len(wired.GetWiredProfileList())
	if not (network_id < num and \
			network_id >= 0):
		print 'Invalid wired network identifier.'
		return False
	else:
		return True

def is_valid_wired_network_profile(profile_name):
	if not profile_name in wired.GetWiredProfileList():
		print 'Profile of that name does not exist.'
		return False
	else:
		return True


def scan_wireless():
	# synchronized scan
	wireless.Scan(True)


def get_current_wireless():
			network_id = wireless.GetCurrentNetworkID(0)
			if is_valid_wireless_network_id(network_id) == True:
				# we're connected to a network, print IP
				print "ID: %s" % network_id
				print "IP: %s" % wireless.GetWirelessIP(0)
				return network_id
			else:
				print "Not connected"
				return -1
			
def wireless_details(network_id):
		if is_valid_wireless_network_id(network_id) == False:
			print "Invalid network_id"
			return

		print "Essid: %s" % wireless.GetWirelessProperty(network_id, "essid")
		print "Bssid: %s" % wireless.GetWirelessProperty(network_id, "bssid")
		if wireless.GetWirelessProperty(network_id, "encryption"):
			print "Encryption: On"
			print "Encryption Method: %s" % \
					wireless.GetWirelessProperty(network_id, "encryption_method")
		else:
			print "Encryption: Off"
		print "Encryption Type (enctype): %s" % wireless.GetWirelessProperty(network_id, "enctype")
		print "Quality: %s" % wireless.GetWirelessProperty(network_id, "quality")
		print "Mode: %s" % wireless.GetWirelessProperty(network_id, "mode")
		print "Channel: %s" % wireless.GetWirelessProperty(network_id, "channel")
		print "Bit Rates: %s" % wireless.GetWirelessProperty(network_id, "bitrates")


def list_encryption_types():
	et = misc.LoadEncryptionMethods()
	#print 'Installed encryption templates:'
	print '%s\t%-20s\t%s' % ('#', 'Name', 'Description')
	id = 0
	for type in et:
		print '%s\t%-20s\t%s' % (id, type['type'], type['name'])
		print '  Req: %s' % str_properties(type['required'])
		print '---'
		# don't print optionals (yet)
		#print '  Opt: %s' % str_properties(type['optional'])
		id += 1
		
def get_wireless_property(network_id, aProperty):
	aProperty = aProperty.lower()
	if is_valid_wireless_network_id(network_id) == False:
		print "Not a valid network_id"
		return

	print wireless.GetWirelessProperty(network_id, aProperty)

def set_wireless_property(network_id, aProperty,set_to):
	aProperty = aProperty.lower()
	if is_valid_wireless_network_id(network_id) == False:
		print "Not a valid network_id"
		return
		
	wireless.SetWirelessProperty(network_id, \
					aProperty, set_to)
def disconnect_wireless():
	daemon.Disconnect()
	if wireless.GetCurrentNetworkID(0) > -1:
			print "Disconnecting from %s on %s" % (wireless.GetCurrentNetwork(0),
					wireless.DetectWirelessInterface())
def save_wireless(network_id):
    if not network_id >= 0:
        return False
    print "Saving:" + str(network_id)
    wireless.SaveWirelessNetworkProfile(network_id)
    return True

def save_current_wireless():
	save_wireless(get_current_wireless())
		
		
##############################################
#Support functions
###############################################
def check_net():
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect(("www.google.com", 80))
			return True

		except socket.error:
			return False
		
def str_properties(prop):
	if len(prop) == 0:
		return "None"
	else:
		#return ', '.join("%s (%s)" % (x[0], x[1].replace("_", " ")) for x in type['required'])
		return ', '.join("%s (%s)" % (x[0], x[1].replace("_", " ")) for x in prop)


def get_ssid2id_dict():
	ssid2id_dict = {}
	for network_id in range(0, wireless.GetNumberOfNetworks()):
		ssid2id_dict[wireless.GetWirelessProperty(network_id, 'essid')] = network_id
	return ssid2id_dict


def translate_encryption_method(method):
	if method == None:
		return
	elif method.lower()[0:3] == "wpa":
		return 'wpa'
	elif method.lower()[0:3] == "wep":
		return 'wep'	
	else:
		return 'not_supported'


###############################################################
#Compounded functions
###############################################################

def connect_wireless(network_id,key):
	#connect and save wless connection with some default dettings
	if is_valid_wireless_network_id(network_id) == False:
		print "Not a valid network_id"
		return

	name = wireless.GetWirelessProperty(network_id, 'essid')
	new_enctype = translate_encryption_method(wireless.GetWirelessProperty(network_id, 'encryption_method'))
	wireless.SetWirelessProperty(network_id, 'enctype', new_enctype)
	wireless.SetWirelessProperty(network_id, 'key', key)

	wireless.SetWirelessProperty(network_id, 'automatic', 1)
	wireless.SetWirelessProperty(network_id, 'use_settings_globally', True)

	enctype = wireless.GetWirelessProperty(network_id, 'enctype')

	print "Connecting to %s with %s on %s" % (name, enctype,
			wireless.DetectWirelessInterface())
	wireless.ConnectWireless(network_id)

	check = lambda: wireless.CheckIfWirelessConnecting()
	message = lambda: wireless.CheckWirelessConnectingMessage()

	# update user on what the daemon is doing
	last = None
	while check():
		next = message()
		if next != last:
			# avoid a race condition where status is updated to "done" after the
			# loop check
			if next == "done":
				break
			print "%s..." % next.replace("_", " ")
			last = next
	print "done!"

	
def connect_wireless_ssid(ssid, key):
	ssid2id_dict = get_ssid2id_dict()
	try:
		network_id = ssid2id_dict[ssid]
	except:
		print "SSID:", ssid, " does not exist"
		return

	connect_wireless(network_id, key)


def get_wireless_networks():
    wlessL = []
    if daemon.GetSignalDisplayType() == 0:
        strenstr = 'quality'
    else:
        strenstr = 'strength'
    for network_id in range(0, wireless.GetNumberOfNetworks()):
        net_dict = {}
        net_dict['network_id'] = network_id 
        	
        connected = wireless.GetCurrentSignalStrength("") != 0 and wireless.GetCurrentNetworkID(wireless.GetIwconfig())==network_id and wireless.GetWirelessIP('') != None
        net_dict['connected'] = connected
        net_dict['bssid'] = wireless.GetWirelessProperty(network_id , 'bssid')
        net_dict['essid'] = wireless.GetWirelessProperty(network_id , 'essid')
        net_dict['signal'] = daemon.FormatSignalForPrinting(str(wireless.GetWirelessProperty(network_id , strenstr)))
        
        if wireless.GetWirelessProperty(network_id , 'encryption'):
            net_dict['encrypt']= wireless.GetWirelessProperty(network_id ,'encryption_method')
        else:
            net_dict['encrypt']= 'None'
        
        net_dict['mode']= wireless.GetWirelessProperty(network_id , 'mode') # Master, Ad-Hoc
        net_dict['channel'] = wireless.GetWirelessProperty(network_id , 'channel')
        
        wlessL.append(net_dict)
        
    return (wlessL)

def print_wireless():
    print '#\tBSSID\t\t\tChannel\tStatus\tESSID\t\tenctype'
    
    wlessL = get_wireless_networks()
    for net_dict in wlessL:
        if net_dict['connected']== True:
            sts = "c"
        else:
            sts = ""
        
		#print net_dict['essid'] +  net_dict['channel'] +  net_dict['encrypt'] + net_dict['signal']
        print '%s\t%s\t%s\t%s\t%s\t\t%s' % (net_dict['network_id'],
            net_dict['bssid'],
            net_dict['channel'],
            sts,
            net_dict['essid'],
            net_dict['encrypt'])
  
########################################################################
daemon, wireless, wired, config = init()

if __name__ == '__main__':

	import getpass

	print "0 Quit"
	print "1 List Wireless networks"
	print "2 Connect to wireless netowork"
	print "3 Test Network"
	print "6 display details"
	print "7 list encryption types"
	print "8 get wireless property"
	print "9 set wireless property"
	print "10 disconnect wireless"
	print "11 Scan"
	print "12 connect to wless on ssid"
	aSelect = raw_input('Please enter a value:')

	if aSelect == "1":
		scan_wireless()
		print_wireless()

	if aSelect == "2":
		aNetwork_id = int(raw_input('Enter network id:'))
		key = raw_input("Enter the encryption key:")
		connect_wireless(aNetwork_id, key)

	if aSelect == "3":
		if check_net() == True:
			print "Network OK"
		else:
			print "Network NOK"

	
	if aSelect == "5":
		aPassword = getpass.getpass("Pls type your password: ")
		install_wicd (aPassword)

	if aSelect == "6":
		aNetwork_id = int(raw_input('Enter network id:'))
		wireless_details(aNetwork_id)

	if aSelect == "7":
		list_encryption_types()

	if aSelect == "8":
		aNetwork_id = int(raw_input('Enter network id:'))
		aProperty = raw_input('Enter property:')
		get_wireless_property(aNetwork_id,aProperty)

	if aSelect == "10":
		disconnect_wireless()

	if aSelect == "12":
		ssid = raw_input('Enter SSID:')
		key = raw_input('Enter the encryption key:')
		scan_wireless()
		connect_wireless_ssid(ssid, key)










