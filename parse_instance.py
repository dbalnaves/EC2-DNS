#!/usr/bin/python
import subprocess
import re
import sys
import json
from pprint import pprint
cmd = subprocess.Popen(['aws','ec2','describe-instances'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out = cmd.communicate()[0]
data = json.loads(out)

cmd = subprocess.Popen(['dig',sys.argv[2],'AXFR','@127.0.0.1'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
dig = cmd.communicate()[0].splitlines()
existing_instances = filter(lambda x:re.search(r'i-[a-z0-9]{8}', x), dig)

print "SERVER 127.0.0.1"
print "ZONE " + sys.argv[2]

for entry in data['Reservations']:
    for item in entry['Instances']:
	if item['VpcId'] == sys.argv[1] and item['State']['Name'] != 'Terminated':
	    print "UPDATE ADD " + item['InstanceId'] + "." + sys.argv[2] + " 3600 A " + item['PrivateIpAddress']
	    for instance in existing_instances:
	        if item['InstanceId'] in instance:
		    existing_instances.remove(instance)
	    exit
	    for i in range(0,len(item['Tags']),1):
		if item['Tags'][i]['Key'] == "DNS":
		    print "UPDATE ADD " + item['Tags'][i]['Value'] + "." + sys.argv[2] + " 3600 CNAME " + item['InstanceId'] + "." + sys.argv[2] + "."
		    for instance in existing_instances:
			if item['Tags'][i]['Value'] in instance:
			    existing_instances.remove(instance)
		    exit
	    exit
    exit
exit

for instance in existing_instances:
    record = re.search(r'(\S+)\s..*', instance)
    print "UPDATE DELETE " + record.group(1)
exit
print "SHOW"
print "SEND"

