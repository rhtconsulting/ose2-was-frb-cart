#READ CLI ARGUMENTS
###############################################################################
OPENSHIFT_WEBSPHERE_IP = sys.argv[0]
OPENSHIFT_WEBSPHERE_WC_ADMINHOST_SECURE_PROXY_PORT = sys.argv[1]

print "echoing argvs"

print OPENSHIFT_WEBSPHERE_IP
print OPENSHIFT_WEBSPHERE_WC_ADMINHOST_SECURE_PROXY_PORT
###############################################################################
#Setup the Console public port to be the Public port assigned by OSE not 9043
###############################################################################

AdminTask.modifyServerPort('server1', '[-nodeName OpenShiftNode01 -endPointName WC_adminhost_secure -host ' +  OPENSHIFT_WEBSPHERE_IP + ' -port ' + OPENSHIFT_WEBSPHERE_WC_ADMINHOST_SECURE_PROXY_PORT + ']')

vhosts = AdminConfig.list('VirtualHost').split(java.lang.System.getProperty("line.separator"))
for vhost in vhosts:
        endpointString = AdminConfig.showAttribute(vhost, "aliases")
        endpointList = endpointString[1:len(endpointString)-1].split(" ")
        #print endpointString
        for endpoint in endpointList:
                #print "%s" %(AdminConfig.showAttribute(endpoint, 'port'));
                #print endpoint

                pound_index = endpoint.index('#')
                split_endpoint = endpoint[pound_index+1:len(endpoint)-1]
                #print endpoint
                if "HostAlias_5"  == split_endpoint:
                  print "%s" %(AdminConfig.showAttribute(endpoint, 'port'));

                  AdminConfig.modify("HostAlias", vhost, [["hostname", "HostAlias_5" ], ["port", OPENSHIFT_WEBSPHERE_WC_ADMINHOST_SECURE_PROXY_PORT]])
###############################################################################
AdminConfig.save()
