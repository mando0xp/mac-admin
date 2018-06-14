#!/usr/bin/python
####################################################################
#
# Written by: Peter Kim
# Date: 5/6/18
# Version: 1
# Description: This script will load a list of computer names
#              and change the computer name from it's current
#              to it's assoicated new name.
#              There is a future option to automate the binding
#              process for Active Directory. This can be enabled
#              for future testing
#
####################################################################

# Import Python modules

import socket, os, sys, subprocess, objc, csv, platform
from Foundation import NSBundle
from time import sleep
from distutils.version import StrictVersion


IOKit_bundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

functions = [("IOServiceGetMatchingService", b"II@"),
             ("IOServiceMatching", b"@*"),
             ("IORegistryEntryCreateCFProperty", b"@I@@I"),
            ]

objc.loadBundleFunctions(IOKit_bundle, globals(), functions)

# Gloabl Variables
serialnumber = ''
name_list = {}
computer_list_file = ""
domain = ""
ou = ""
ad_user = ""
ad_password = ""
osver = platform.mac_ver()[0]

def io_key(keyname):
    return IORegistryEntryCreateCFProperty(IOServiceGetMatchingService(0, IOServiceMatching("IOPlatformExpertDevice".encode("utf-8"))), keyname, None, 0)

def get_hardware_serial():
    return io_key("IOPlatformSerialNumber".encode("utf-8"))

def admincheck(user):
    global adminstatus
    adminstatus = os.system("dscl . -read /Groups/admin | grep " + user)
    if adminstatus == 0:
        print user + " has admin rights..."
    else:
        print user + " does not have admin rights..."

# Change the all computer and hostnames
def change_hostname(name):
    print "Changing computer name to " + name + "..."
    os.system("scutil --set HostName " + name)
    os.system("scutil --set ComputerName " + name)
    os.system("scutil --set LocalHostName " + name)

def removefiles(listfile):
    print "Removing computernames.csv..."
    os.system("rm " + listfile)

# Unbind machine from AD
def unbind(username, password):
    print "Unbinding from AD..."
    os.system("dsconfigad -f -r -u " + username + " -p " + password)

# Bind machine to AD
# This will call a custom trigger from JAMF to bind the computer
def bind():
    print "Calling JAMF Policy to bind to AD..."
    os.system("jamf policy -trigger bindtoad")

# Restart opendirectoryd Service	
def restartdirectory():
    print "Restarting opendirectoryd service..."
    os.system("killall opendirectoryd")
    
# Delete old account, move the home directory, and change ownership
def deleteuser(user):
    print "Moving home folder..."
    os.system("mv /Users/" + user + " /Users/old_" + user)
    print "Deleting user profile..."
    os.system("dscl . -delete /Users/" + user)

# Rename the home directory to the LAN ID and change the permissions to the LAN ID
# Create a mobile account
# Make the user an Admin
def migrateuser(user,new_user):
    print "Migrating home folder to LAN ID"
    os.system("mv /Users/old_" + user + " /Users/" + new_user)
    print "Changing ownership to the home folder..."
    os.system("chown -R " + new_user + " /Users/" + new_user)
    if adminstatus == 0:
        print user + " is a part of the admin group"
        print "Adding LAN ID to the Admin group..."
        os.system("dseditgroup -o edit -a " + new_user + " -t user admin")
    else:
        print user + "was not an admin..."
    if StrictVersion(osver) >= StrictVersion('10.13.4')
        print "Please continue with manual configuration from creating mobile account..."
    else:
        print "Creating mobile account for LAN ID..."
        os.system("/System/Library/CoreServices/ManagedClient.app/Contents/Resources/createmobileaccount -n " + new_user)
#############################################################
# Main Section of the script                                #
#############################################################

# Load the file
reader = csv.reader(open(computer_list_file, 'r'))

for row in reader:
    k, v, v2, v3 = row
    name_list[k] = [v, v2, v3]

serialnumber = get_hardware_serial()

# Print the list of current computer names and associated new names
# print name_list

# Check if the hostname is in the computer_names.txt
# Change computer name to new associated computer name
if serialnumber in name_list:
    name = name_list.get(serialnumber)
    compname = name[0]
    user = name[1]
    new_user = name[2].lower()
    unbind(ad_user,ad_password)
    change_hostname(compname)
    admincheck(user)
    deleteuser(user)
    bind()
    print "Sleep for 20 seconds..."
    sleep(20)
    restartdirectory()
    print "Sleep for 20 seconds..."
    sleep(20)
    migrateuser(user,new_user)

# Exit with message if the computer name is not in the list
else:
    sys.exit("Computer does not exist")

removefiles(computer_list_file)
