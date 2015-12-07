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
                  #AdminConfig.modify("HostAlias", vhost, [["hostname", "HostAlias_5" ], ["port", OPENSHIFT_WEBSPHERE_WC_ADMINHOST_SECURE_PROXY_PORT]])
                  AdminConfig.modify(endpoint, [['port', OPENSHIFT_WEBSPHERE_WC_ADMINHOST_SECURE_PROXY_PORT]])
###############################################################################

###############################################################################
# Configure WebSphere to use a specific IP address
# http://www-01.ibm.com/support/knowledgecenter/SSAW57_8.5.5/com.ibm.websphere.nd.doc/ae/trun_multiplenic.html?lang=en
###############################################################################
# Customize ORB service
orb = AdminConfig.list('ObjectRequestBroker')
orbPropertiesString = AdminConfig.showAttribute(orb, "properties")
orbPropertiesList = orbPropertiesString[1:len(orbPropertiesString)-1].split(" ")
# Remove specific existing properties
for orbProperty in orbPropertiesList:
        name = AdminConfig.showAttribute(orbProperty, "name")
        if name == "com.ibm.CORBA.LocalHost":
                AdminConfig.remove(orbProperty)
        elif name == "com.ibm.ws.orb.transport.useMultiHome":
                AdminConfig.remove(orbProperty)

# Add new properties
attr = []
attr.append([['name','com.ibm.CORBA.LocalHost'],['required','true'],['value', OPENSHIFT_WEBSPHERE_IP]])
AdminConfig.modify(orb, [['properties', attr]])
attr = []
attr.append([['name','com.ibm.ws.orb.transport.useMultiHome'],['required','false'],['value','false']])
AdminConfig.modify(orb, [['properties', attr]])

# Customize JVM custom properties
jvm = AdminConfig.list('JavaVirtualMachine')
jvmPropertiesString = AdminConfig.showAttribute(jvm, "systemProperties")
jvmPropertiesList = jvmPropertiesString[1:len(jvmPropertiesString)-1].split(" ")
# Remove specific existing properties
for jvmProperty in jvmPropertiesList:
        name = AdminConfig.showAttribute(jvmProperty, "name")
        if name == "com.ibm.websphere.network.useMultiHome":
                AdminConfig.remove(jvmProperty)
# Add new properties
attr = []
attr.append([['name','com.ibm.websphere.network.useMultiHome'],['required','false'],['value', 'false']])
AdminConfig.modify(jvm, [['systemProperties', attr]])

# Bind all ports to GEAR IP
endpoints = AdminConfig.list('EndPoint').split(java.lang.System.getProperty("line.separator"))
for endpoint in endpoints:
	AdminConfig.modify(endpoint, '[[host ' + OPENSHIFT_WEBSPHERE_IP + ']]')

###############################################################################

AdminConfig.save()

