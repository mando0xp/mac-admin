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
import socket, os, sys,argparse, objc, csv
from Foundation import NSBundle

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
new_computer_list_file = "/tmp/newcomputernames.csv"
domain = "domain"
ou = "CN=Computers,DC=domain"
ad_user = ""
ad_password = ""

def io_key(keyname):
    return IORegistryEntryCreateCFProperty(IOServiceGetMatchingService(0, IOServiceMatching("IOPlatformExpertDevice".encode("utf-8"))), keyname, None, 0)

def get_hardware_serial():
    return io_key("IOPlatformSerialNumber".encode("utf-8"))

# Change the all computer and hostnames
def change_hostname(name):
	os.system("scutil --set HostName " + name)
	os.system("scutil --set ComputerName " + name)
	os.system("scutil --set LocalHostName " + name)

def removefiles(listfile,newlistfile):
	os.system("rm " + listfile + " " + newlistfile)

# # Unbind machine from AD
# def unbind(username, password)
# 	os.system("dsconfig -f -r -u " + username + " -p " + password)

# # Bind machine to AD
# def bind(computername,username,password)
# 	os.system("dsconfigad -a " + computername + " -domain " + domain +  " -u " + username + " -p " + password + " -ou " + ou)

#############################################################
# Main Section of the script                                #
#############################################################


parser = argparse.ArgumentParser()
parser.add_argument("--aduser", help="Enter your domain admin account or service account")
parser.add_argument("--adpassword", help="Enter your domain admin or service account password")
args = parser.parse_args()

# Check if ad_user is entered or exit
if args.aduser:
	ad_user = args.aduser
elif ad_user != "":
	print "AD Account: " + ad_user
else:
	sys.exit("Please enter a username")

# Check if ad_password is entered
if args.adpassword:
	ad_password = args.adpassword
elif ad_password != "":
	print "Password stored..."
else:
	sys.exit("No password was entered")

# Load the file
with open(computer_list_file, mode='r') as infile:
    reader = csv.reader(infile)
    with open(new_computer_list_file, mode='w') as outfile:
        writer = csv.writer(outfile)
        name_list = {rows[0]:rows[1] for rows in reader}

serialnumber = get_hardware_serial()

# Print the list of current computer names and associated new names
# print name_list

# Check if the hostname is in the computer_names.txt
# Change computer name to new associated computer name
if serialnumber in name_list:
	new_hostname = name_list.get(serialnumber)
	# print "Unbinding from AD..."
	# unbind(ad_user,ad_password)
	print "Computer exists, changing name to " + new_hostname
	change_hostname(new_hostname)
	# print "Binding to AD..."
	# bind(new_hostname,ad_user,ad_password)
# Exit with message if the computer name is not in the list
else:
	sys.exit("Computer does not exist")

removefiles(computer_list_file,new_computer_list_file)