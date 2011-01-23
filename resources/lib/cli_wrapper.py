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

import optparse
import sys
import qf_wicd_wrapper

parser = optparse.OptionParser()

parser.add_option('--connect', '-c', default=False, action='store_true')
parser.add_option('--list', '-l', default=False, action='store_true')
parser.add_option('--ssid', '-s')
parser.add_option('--id', '-i')
parser.add_option('--key', '-k')
parser.add_option('--test', '-t', default=False, action='store_true')


options, arguments = parser.parse_args()
ssid = options.ssid  
id = options.id  
key = options.key


if options.connect and not id == None:
    id = int(id)
    print 'Connecting...'
    qf_wicd_wrapper.connect_wireless(id,key)
    print 'Done connecting...'
    print 'saving'
    #Daemon saves on connect automatically
    #qf_wicd_wrapper.save_wireless(id)

elif options.connect and not ssid == None and id == None:
    print 'Scanning....'
    qf_wicd_wrapper.scan_wireless()
    print 'Connecting...'
    qf_wicd_wrapper.connect_wireless_ssid(ssid,key)
    print 'Done connecting...'
    print 'saving'
    #dont user save current...connection may have failed.....
    # and daemon saves on connect eitherway.....
    #qf_wicd_wrapper.save_current_wireless()

elif options.list and not options.test:
    qf_wicd_wrapper.scan_wireless()
    wlessL = qf_wicd_wrapper.get_wireless_networks()
    for net_dict in wlessL:
        print str(net_dict['network_id']) + ";" + \
            net_dict['essid'] + ";" +\
            net_dict['channel'] + ";" +\
            str(net_dict['connected']) + ";" +\
            net_dict['signal'] + ";" +\
            net_dict['encrypt']
            
elif options.list and  options.test:
    print "0;1969;8;True;57%;WPA2"
    print "1;blabla_Blablabla;1;False;21%;None"
    print "2;default;1;False;21%;None"

else:
    print 'Nothing to do'
