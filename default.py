import sys
import os
import xbmc
import xbmcaddon


__scriptid__   = "script.linux.wireless"
__settings__   = xbmcaddon.Addon(id=__scriptid__)
__language__   = __settings__.getLocalizedString
__version__    = __settings__.getAddonInfo('version')
__cwd__        = __settings__.getAddonInfo('path')
__scriptname__ = "Wireless Manager"
__author__     = "VIKJON0"

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)

print "[SCRIPT] '%s: version %s' initialized!" % (__scriptname__, __version__, )

if (__name__ == "__main__"):
    import gui
## To do - chnage name of xml (skins /default)
    ui = gui.GUI( "script_linux_wireless-main.xml" , __cwd__ , "Default")
    del ui

sys.modules.clear()
