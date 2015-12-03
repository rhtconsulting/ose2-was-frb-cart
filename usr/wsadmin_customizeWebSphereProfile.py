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

###############################################################################
AdminConfig.save()
