import sys
import os
import xbmc
import xbmcaddon
import xbmcgui
import qf_wicd_installer
import socket

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__settings__ = sys.modules[ "__main__" ].__settings__
__cwd__ = sys.modules[ "__main__" ].__cwd__

#enable localization
getLS   = sys.modules[ "__main__" ].__language__

#TODO There seem to be a problem when multiple network have auto=1 and some of them are too weak or have to wrong key
#TODO Display indicator for auto = 1


class GUI(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        self.doModal()


    def onInit(self):
        #xbmcgui.lock()
        self.defineControls()

        self.status_msg = ""
        self.status_label.setLabel("")

        self.hidden_button.setEnabled(False)
        self.details_button.setEnabled(False)
	
        self.showDialog()
                
        if qf_wicd_installer.check_installed() == True:
            self.status_msg = self.status_msg + " " + "Wicd is installed!"
            self.install_button.setEnabled(False)
        else:
            self.status_msg = self.status_msg + " " + "Wicd is not installed!"
         
	#To slow to check internet on init (when not existing)   
        #if self.check_net() == True:
        #    self.status_msg = self.status_msg + " " + "You have internet connection!"
        #else:
        #    self.status_msg = self.status_msg + " " + "You do not have internet connection!"

        #self.status_label.setLabel(self.status_msg)
       
        #xbmcgui.unlock()
        
    def defineControls(self):
        #actions
        self.action_cancel_dialog = (9, 10)
        #control ids
        self.control_heading_label_id         = 2
        self.control_list_label_id            = 3
        self.control_list_id                  = 10
        self.control_hidden_button_id         = 11
        self.control_details_button_id        = 13
        self.control_connect_button_id        = 14
        self.control_install_button_id        = 18
        self.control_cancel_button_id         = 19
        self.control_status_label_id          = 100
        
        #controls
        self.heading_label      = self.getControl(self.control_heading_label_id)
        self.list_label         = self.getControl(self.control_list_label_id)
        self.list               = self.getControl(self.control_list_id)
        self.hidden_button      = self.getControl(self.control_hidden_button_id)
        self.connect_button     = self.getControl(self.control_connect_button_id)
        self.details_button     = self.getControl(self.control_details_button_id)
        self.install_button     = self.getControl(self.control_install_button_id)
        self.cancel_button      = self.getControl(self.control_cancel_button_id)
        self.status_label       = self.getControl(self.control_status_label_id)

    def showDialog(self):
        self.updateList()

    def closeDialog(self):
        self.close()

    def onClick(self, controlId):
        self.status_msg = ""
        self.status_label.setLabel(self.status_msg)
        
        #Connect from list
        if controlId == self.control_list_id:
            position = self.list.getSelectedPosition()
            self.connect_wireless(position)
            msg = "Refreshing...." 
            self.status_label.setLabel(msg)
            self.updateList()
	    msg = "Done!" 
            self.status_label.setLabel(msg) 
       
        #Connect button
        elif controlId == self.control_connect_button_id:
            position = self.list.getSelectedPosition()
            self.connect_wireless(position)
            msg = "Refreshing...." 
            self.status_label.setLabel(msg)
            self.updateList()
	    msg = "Done!" 
            self.status_label.setLabel(msg)
        
        #install
        elif controlId == self.control_install_button_id:
            return_msg =  self.install()
        
        #cancel dialog
        elif controlId == self.control_cancel_button_id:
            self.closeDialog()

    
    def onAction(self, action):
        if action in self.action_cancel_dialog:
            self.closeDialog()

    def onFocus(self, controlId):
        pass

    def Connect(self):
        position = self.list.getSelectedPosition()
    
    def get_wireless_networks(self):
        pytBin = "/usr/bin/python -E"
        cliWrapperPath = os.getcwd() + "/resources/lib/cli_wrapper.py "
        #param = " --list --test "
        param = " --list "
        
        cmd = pytBin + " " + cliWrapperPath + param

        print "Calling Cli Wrapper: " +  cmd 
        (stdin, stdout, stderr) = os.popen3(cmd)#, mode, bufsize)
        
        #rebuild the list
        wlessL = []
        for line in stdout.readlines():
            #put the dictionary back together
            net_dict = {}
            keys = ['network_id','essid','channel','connected','signal','encrypt']
            values = line.split(';')
            
            net_dict = dict(zip(keys, values))
            if net_dict['connected'] == 'True':
                net_dict['connected'] = True
            else:
                 net_dict['connected'] = False
        
            wlessL.append(net_dict)
    
        s = stdout.read()
        print "stdout####"
        print s

        print "stderr####"
        s = stderr.read()
        print s
        
        return (wlessL)
    
    def connect_wireless(self, network_id):
        #Check if wicd is installed    
        if qf_wicd_installer.check_installed() == False:
            msg = _( 30105 )  
            self.status_label.setLabel(msg)
            return

        #Prompt for key
        key = ""

        kb = xbmc.Keyboard("", _( 30104 ), False)
        kb.doModal()
        if (kb.isConfirmed()):
            key=kb.getText()
            
        if  key == "":
            msg = _( 30109 )  
            self.status_label.setLabel(msg)
            return
        
        msg = "Connecting....."  
        self.status_label.setLabel(msg)
        #attempt to connect   
        #xbmcgui.lock()     
        pytBin = "/usr/bin/python -E"
        cliWrapperPath = os.getcwd() + "/resources/lib/cli_wrapper.py "
        param = " --connect --key=" +  key + " --id=" + str(network_id)
        cmd = pytBin + " " + cliWrapperPath + param

        #print "Calling Cli Wrapper: " +  cmd 
        (stdin, stdout, stderr) = os.popen3(cmd)#, mode, bufsize)
        
        s = stdout.read()
        print "stdout####"
        print s

        print "stderr####"
        s = stderr.read()
        print s

	msg = "Finished connecting" 
        self.status_label.setLabel(msg)
        #xbmcgui.unlock()
        
        return


    def updateList(self):
        self.list.reset()
        wlessL = self.get_wireless_networks()
        
        for net_dict in wlessL:
            if net_dict['connected'] == True:
                sts = '>'
            else:
                sts = ''
                
            item = xbmcgui.ListItem (label=sts, label2 = net_dict['essid'])
            item.setProperty('id',net_dict['network_id'])
            item.setProperty('channel',net_dict['channel'])
            item.setProperty('encryption',net_dict['encrypt'])
            item.setProperty('signal',net_dict['signal'])
            self.list.addItem(item)
        
                
    def install( self ):
        self.status_msg = ""
        self.status_label.setLabel(self.status_msg)
        
        if self.check_net() == False:
            self.status_label.setLabel("Internet not available"  )
            return

        user  = __settings__.getSetting( "user" )

        aPassword = ""
        kb = xbmc.Keyboard("", _( 30101 ), True)

        kb.doModal()
        if (kb.isConfirmed()):
            aPassword=kb.getText()

        if not aPassword == "":
            msg = _( 30102 )  
            self.status_label.setLabel(msg)
             
            qf_wicd_installer.install_wicd(user, aPassword)
            
            if qf_wicd_installer.check_installed() == True:
                msg = _( 30106 )
                self.install_button.setEnabled(False)
            else:
                msg = _( 30105 )
        else:
            # No pwd
            msg = _( 30107 )  
        self.status_label.setLabel(msg)
        return  

    def check_net(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("www.google.com", 80))
            return True
        except socket.error:
            return False

