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
import socket
import os
import sys

# Gloabl Variables
hostname = socket.gethostname()
name_list = {}
computer_list_file = "/tmp/computer_names.txt"
domain = "domain"
ou = "CN=Computers,DC=domain"

# Load and format computer list
def load_hostname():
	file = open(computer_list_file, "r")
	for line in file:
		name_split = line.split(":")
		name_key = name_split[0]
		name_value = name_split[1]
		name_length_format = len(name_value)-1
		name_format = name_value[0:name_length_format]
		name_list[name_key] = name_format

# Change the all computer and hostnames
def change_hostname(name):
	os.system("scutil --set HostName " + name)
	os.system("scutil --set ComputerName " + name)
	os.system("scutil --set LocalHostName " + name)

# # Unbind machine from LV AD
# def unbind(username, password)
# 	os.system("dsconfig -f -r -u " + username + " -p " + password)

# # Bind machine to NM AD
# def bind(computername,username,password)
# 	os.system("dsconfigad -a " + computername + " -domain " + domain +  " -u " + username + " -p " + password + " -ou " + ou)

#############################################################
# Main Section of the script                                #
#############################################################

# Load the file
load_hostname()

# Print the list of current computer names and associated new names
# print name_list

# Check if the hostname is in the computer_names.txt
# Change computer name to new associated computer name
if hostname in name_list:
	new_hostname = name_list.get(hostname)
	# print "Unbinding from AD..."
	# unbind(ad_service,password)
	print "Computer exists, changing name to " + new_hostname
	change_hostname(new_hostname)
	# print "Binding to AD..."
	# bind(new_hostname,ad_service,password)
# Exit with message if the computer name is not in the list
else:
	sys.exit("Computer does not exist")

