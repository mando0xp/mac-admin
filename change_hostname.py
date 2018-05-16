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

import socket, os, sys, subprocess, argparse, objc, csv
from Foundation import NSBundle
from time import sleep


IOKit_bundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

functions = [("IOServiceGetMatchingService", b"II@"),
             ("IOServiceMatching", b"@*"),
             ("IORegistryEntryCreateCFProperty", b"@I@@I"),
            ]

objc.loadBundleFunctions(IOKit_bundle, globals(), functions)

# Gloabl Variables
serialnumber = ''
name_list = {}
computer_list_file = "/tmp/computernames.csv"
domain = "nm.nmfco.com"
ou = "CN=Computers,DC=nm,DC=nmfco,DC=com"
lvad_user = "lv-it"
lvad_password = "password"
nmad_user = "nun8175-nm"
nmad_password = "Summer68"

def io_key(keyname):
    return IORegistryEntryCreateCFProperty(IOServiceGetMatchingService(0, IOServiceMatching("IOPlatformExpertDevice".encode("utf-8"))), keyname, None, 0)

def get_hardware_serial():
    return io_key("IOPlatformSerialNumber".encode("utf-8"))

# Change the all computer and hostnames
def change_hostname(name):
	os.system("scutil --set HostName " + name)
	os.system("scutil --set ComputerName " + name)
	os.system("scutil --set LocalHostName " + name)

def removefiles(listfile):
	os.system("rm " + listfile)

# Unbind machine from AD
def unbind(username, password):
	os.system("dsconfigad -f -r -u " + username + " -p " + password)

# Bind machine to AD
def bind(computername,username,password):
	os.system("dsconfigad -a " + computername + " -domain " + domain +  " -u " + username + " -p " + password + " -ou " + ou)

# Delete old account, move the home directory, and change ownership
def deleteuser(lvuser):
	homedir = subprocess.check_output("/usr/bin/dscl . read /Users/" + lvuser + " NFSHomeDirectory | /usr/bin/cut -c 19-", shell=True)
	os.system("mv " + homedir + " /Users/old_" + lvuser)
	os.system("dscl . -delete /Users/" + lvuser)

def migrateuser(lvuser,nmuser):
	os.system("mv /Users/old_" + lvuser + " /Users/" + nmuser)
	os.system("chown -R " + nmuser + " /Users/" + nmuser)
	os.system("/System/Library/CoreServices/ManagedClient.app/Contents/Resources/createmobileaccount -n " + nmuser)
	os.system("dseditgroup -o edit -a " + nmuser + " -t user admin")
#############################################################
# Main Section of the script                                #
#############################################################


parser = argparse.ArgumentParser()
parser.add_argument("--lvaduser", help="Enter your LV domain admin account or service account")
parser.add_argument("--lvadpassword", help="Enter your LV domain admin or service account password")
parser.add_argument("--nmaduser", help="Enter your NM domain admin account or service account")
parser.add_argument("--nmadpassword", help="Enter your NM domain admin or service account password")
args = parser.parse_args()

# Check if LV Domain or Service Account is entered or exit
if args.lvaduser:
	lvad_user = args.lvaduser
elif lvad_user != "":
	print "AD Account: " + lvad_user
else:
	sys.exit("Please enter a LV Domain or Service Account")

# Check if ad_password is entered
if args.lvadpassword:
	lvad_password = args.lvadpassword
elif lvad_password != "":
	print "Password stored..."
else:
	sys.exit("No password was entered")

# Check if NM Domain or Service Account is entered or exit
if args.nmaduser:
	nmad_user = args.nmaduser
elif nmad_user != "":
	print "AD Account: " + nmad_user
else:
	sys.exit("Please enter a NM Domain or Service Account")

# Check if ad_password is entered
if args.nmadpassword:
	nmad_password = args.nmadpassword
elif nmad_password != "":
	print "Password stored..."
else:
	sys.exit("No password was entered")

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
	nmcomp = name[0]
	lvuser = name[1]
	nmuser = name[2]
	print "Unbinding from AD..."
	unbind(lvad_user,lvad_password)
	print "Computer exists, changing name to " + nmcomp
	change_hostname(nmcomp)
	print "Deleting user " + lvuser + "..."
	deleteuser(lvuser)
	print "Binding to AD..."
	bind(nmcomp,nmad_user,nmad_password)
	print "Sleep for 20 seconds"
	sleep(20)
	print "Moving data to " + nmuser
	migrateuser(lvuser,nmuser)

# Exit with message if the computer name is not in the list
else:
	sys.exit("Computer does not exist")

removefiles(computer_list_file)
