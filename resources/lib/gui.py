import sys
import os
import xbmc
import xbmcaddon
import xbmcgui
import socket
from compiler.ast import Return
import qf_wicd_wrapper

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__settings__ = sys.modules[ "__main__" ].__settings__
__cwd__ = sys.modules[ "__main__" ].__cwd__

#enable localization
getLS   = sys.modules[ "__main__" ].__language__


#TODO Connect to hidden network
#TODO Re-add connect button and add connect dialog with more options
#TODO Display network detail window

class GUI(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        self.doModal()


    def onInit(self):
        self.defineControls()

        self.status_msg = ""
        self.status_label.setLabel(self.status_msg)
	
        self.showDialog()
                
        self.status_label.setLabel(self.status_msg)
       
        
    def defineControls(self):
        #actions
        self.action_cancel_dialog = (9, 10)
        #control ids
        self.control_heading_label_id         = 2
        self.control_list_label_id            = 3
        self.control_list_id                  = 10
        self.control_scan_button_id           = 11
        self.control_disconnect_button_id     = 13
        self.control_remove_auto_button_id    = 14
        self.control_install_button_id        = 18
        self.control_cancel_button_id         = 19
        self.control_status_label_id          = 100
        
        #controls
        self.heading_label      = self.getControl(self.control_heading_label_id)
        self.list_label         = self.getControl(self.control_list_label_id)
        self.list               = self.getControl(self.control_list_id)
        self.scan_button        = self.getControl(self.control_scan_button_id)
        self.remove_auto_button = self.getControl(self.control_remove_auto_button_id)
        self.disconnect_button  = self.getControl(self.control_disconnect_button_id)
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
            msg = getLS(30115) #Refreshing
            self.status_label.setLabel(msg)
            self.updateList()
            msg = getLS(30116) #Done
            self.status_label.setLabel(msg) 
       
        #remove auto button
        elif controlId == self.control_remove_auto_button_id:
            position = self.list.getSelectedPosition()
            self.remove_auto(position)
            msg = getLS(30115) #Refreshing
            self.status_label.setLabel(msg)
            self.updateList()
            msg = getLS(30116) #Done
            self.status_label.setLabel(msg)
        
        #scan button
        elif controlId == self.control_scan_button_id:
            msg = getLS(30115) #Refreshing
            self.status_label.setLabel(msg)
            self.updateList()
            msg = getLS(30116) #Done
            self.status_label.setLabel(msg)
        
        #disconnect button
        elif controlId == self.control_disconnect_button_id:
            msg = getLS(30117) #Disconnecting
            self.status_label.setLabel(msg)
            self.disconnect()
            
            msg = getLS(30115) #Refreshing
            self.status_label.setLabel(msg)
            self.updateList()
            
            msg = getLS(30116) #Done
            self.status_label.setLabel(msg)
            
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
    
   
    def connect_wireless(self, network_id):
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
        
        msg = getLS(30118) #Connecting
        self.status_label.setLabel(msg)

        qf_wicd_wrapper.connect_wireless(network_id,key)

        msg = getLS(30113) #connection attempt made
        self.status_label.setLabel(msg)
        
        return


    def disconnect(self):
        qf_wicd_wrapper.disconnect_wireless()
        return


    def remove_auto(self, network_id):
        msg = getLS(30119) #Configuring
        self.status_label.setLabel(msg)
     
        qf_wicd_wrapper.remove_auto(network_id)
     
        msg = getLS(30116) #Done
        self.status_label.setLabel(msg)   
        return


    def updateList(self):
        print "updating list"
        self.list.reset()
        
        qf_wicd_wrapper.scan_wireless()
        wlessL = qf_wicd_wrapper.get_wireless_networks()
        
        
        for net_dict in wlessL:
            if net_dict['connected'] == True:
                sts = '>'
            elif net_dict['automatic'] == '1':
                sts = 'a'
            else:
                sts = ''
                
            item = xbmcgui.ListItem (label=sts, label2 = net_dict['essid'])
            item.setProperty('channel',net_dict['channel'])
            item.setProperty('encryption',net_dict['encrypt'])
            item.setProperty('signal',net_dict['signal'])
            self.list.addItem(item)
    
    
            
