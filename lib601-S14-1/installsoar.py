#!/usr/bin/python

from sys import argv
import os.path
from distutils import sysconfig
def getProgramsMenuPath():
    """getProgramsMenuPath() -> String|None
    @return the filesystem location of the common Start Menu.
    """
    
    try:
        return get_special_folder_path("CSIDL_COMMON_PROGRAMS")
    except OSError: # probably Win98
        return get_special_folder_path("CSIDL_PROGRAMS")

if argv[1] == '-install':
    try:
        print "Installing shortcut"
        exec_dir=sysconfig.get_config_var("exec_prefix")
        print "Python in "+exec_dir
        menu_path=getProgramsMenuPath()
        print "Programs menu in "+menu_path
        #soar_shortcut_path="SoaR.lnk"
        soar_shortcut_path=os.path.join(menu_path, "soar.lnk")
        print "soar shortcut installing to "+soar_shortcut_path
        soar_shortcut_path=os.path.join(menu_path, "soar.lnk") 
        #CMax_shortcut_path="CMax.lnk"
        CMax_shortcut_path=os.path.join(menu_path, "CMax.lnk")
        print "CMax shortcut installing to "+CMax_shortcut_path
        CMax_shortcut_path=os.path.join(menu_path, "CMax.lnk")               
        
        create_shortcut(os.path.join(exec_dir, "python.exe"),
                        "soar",
                        soar_shortcut_path,
			'-Qnew -c "import form.main;import soar;import soar.application;form.main.Application(soar.application.application)"')
        create_shortcut(os.path.join(exec_dir, "python.exe"),
                        "CMax",
                        CMax_shortcut_path,
			os.path.join(exec_dir, "Lib\site-packages\lib601\CMaxMain.pyc"))
        print "Done"
    except:
        print sys.exc_info()
else:
    print "This script is designed to be run from the Windows installer."

