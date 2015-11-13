IBM WebSphere Application Server on OpenShift Handbook
======================================================

A. Synopsis
===========

What this is about
------------------
This project represents the source code of the Websphere 8.5.5.1 OpenShift Enterprise cartridge. It is meant to be loaded into OpenShift from source code. There are a few installation steps that are outside OpenShift regarding the installation of IBM's WebSphere but also directory persmissions and SELinux policy enablement.

The cartridge currently supports the following features:

* Provisioning of new IBM WebSphere Application Server instance in minutes
* Full build & Deploy life cycle (as with EAP cartridge)
* Hot Deployment

Screenshots
------------------
![1. Create new Gear](./usr/doc/01_ose_create_new_gear.png)

![2. Select WebSphere Application Server Cartridge](./usr/doc/02_ose_create_new_was_cart.png)

![3. Cartridge creation is finished](./usr/doc/03_ose_create_new_was_cart_finished.png)

![4. Overview of newly created application](./usr/doc/04_was_application_overview.png)

![5. View of created sample application](./usr/doc/05_application_demo.png)

![6. Demo of WebSphere Admin Console](./usr/doc/06_was_admin_console.png)


B. Installation
===============

1. Setup OSE Environment
------------------------

The setup of the OSE Environment can be accomplished as per your usual way of deploying broker and nodes. This could be via the OSE install script, or any other CM tools like Puppet and Ansible


2. WebSphere Application Server Installation
--------------------------------------------

### IMPORTANT NOTES
In contradiction to the deployment model of other cartridges (that includes all binaries of a certain technology), we've decided not to put the installation files into the cartridge. The reasoning behind:

* IBM WebSphere Application Server Binaries are very large (around 2-3 GB)
* Installation process for the binaries takes takes a long time (up to 15 minutes according to the computing resources)


### Binary Installation
The installation of IBM WebSphere on the filesystem can be done either via the IBM agent installer or any other means that are currently emplyed. The main thing to note here is that profile creation inside the IBM WAS installation would need to be enabled to allow non root users to create them. That is because each gear in OSE will create its own profile and each gear runs as its own UUID and not as root.

### Non-Root permissions
In order to create profiles by non-root users, special file permission settings have to be set on your WebSphere installation. Please follow the steps described here: http://www-01.ibm.com/support/knowledgecenter/SS7JFU_8.5.5/com.ibm.websphere.express.doc/ae/tpro_nonrootpro.html?lang=en

We have included the setWebSpherePermissionsForNonRootProfileCreation.sh that sets basic file permissions on the diretories that gears would require to access. 

###SELinux Permissions

With SELinux enabled on the system, we will require that the following group context be set on the IBM WAS AppServer directory. This would ensure that gear that run under the openshift_rw_file_t group context can have read/write permissions to shared directories under IBM WAS. This does not mean that gears will be able to step on each other in these shared dirs since each gear will have ownership of its own files.


3. Customize SELinux Configuration
----------------------------------
Since IBM WebSphere Application is installed outside of the gear's sandbox, you need to customize SELinux permission settings in a way that the installation directory "/opt/IBM/WebSphere/AppServer" can be accessed with read/write.

```
semanage fcontext -a -t openshift_rw_file_t "/path-to/IBM/WebSphere/AppServer(/.*)?"
restorecon -R -v /path-to/IBM/WebSphere/AppServer/
```


4. Cartridge Installation
-------------------------
The cartridge can be installed as any other  OSE cartridge. However, you MUST have to make sure that WebSphere Application Server has been installed before (as described in the preceding sections):

Extract the zipped source code of the WAS cartridge under ```/usr/libexec/openshift/cartridges```

You will also need to set the correct SELinux Context on the cartridge so that it is consitent with the rest of the cartrdiges on each node. This file context is:

```system_u:object_r:bin_t:s0```

To set this context run the following command:

```chcon -R -u system_u /usr/libexec/openshift/cartrdiges/ose2-was-frb-cart``` 

On each OpenShift node where you wish to make this cartridge available execute the following commands:

```
cd /usr/libexec/openshift/cartridges
oo-admin-cartridge --action install --recursive --source /usr/libexec/openshift/cartridges
```

To make the cartridge available run this commmand from the broker:

```oo-admin-ctl-cartridge --activate -c import-node node.hostname```

B. Administration and configuration
===================================

Configure a custom installation location for IBM WebSphere Application Server
-----------------------------------------------------------------------------
This cartridge needs an existing installation of the WebSpehere Application Server on each of your nodes. You need to define the location of the installation through a system wide environment variable

```
echo "/opt/IBM/WebSphere/AppServer" > /etc/openshift/env/OPENSHIFT_WEBSPHERE_INSTALL_LOCATION
```

this will make sure that the cartridge finds the necessary components.


Configure non-root file permissions
-----------------------------------
The file permissions of your WebSphere installation must be set to allow non-root profile creation (see official IBM documentation: http://www-01.ibm.com/support/knowledgecenter/SS7JFU_8.5.5/com.ibm.websphere.express.doc/ae/tpro_nonrootpro.html?lang=en). This has to be done once per binary installation. You can use the following script as a basis for automating this: "usr/setWebSpherePermissionsForNonRootProfileCreation.sh"


How profile creation works
--------------------------
This cartridge will call `${OPENSHIFT_WEBSPHERE_DIR}/install/bin/manageprofiles.sh` and create a profile with the name of the OpenShift app that the user created followed by the domain space name. The final format looks like: "APP-NAME-DOMAIN" . The profile will be created underneath the `profile` directory inside your gears `data` directory.

The profile will have security enabled. An admin `username` and a `password` are generated at the time of creation and the `PerfTuningSetting` will be set to development.


Access to WebSphere Admin Console
---------------------------------
PREFFERED - Option 1) After you have created your gear, do a `rhc port-forward <GEAR_NAME>` and open a browser with the following URL `https://<YOUR_LOCAL_IP>:9043/ibm/console`.

Option 2) The Admin Console is also exposed via a separate external port that can be determined as follows:

```
rhc ssh <GEAR_NAME>
export | grep WC_ADMINHOST_SECURE_PROXY_PORT
```

Now point your browser to the following URL: `https://<GEAR_DNS>:<WC_ADMINHOST_SECURE_PROXY_PORT>/ibm/console/logon.jsp` and enter your credentials. Unfortunately the Admin Console tries to redirect us to the local port 9043. 

Now manually change port 9043 back to WC_ADMINHOST_SECURE_PROXYPORT and change login.jsp to login.do so that the URL looks like follows: `https://<GEAR_DNS>:<WC_ADMINHOST_SECURE_PROXY_PORT>/ibm/console/login.do?action=secure`.

The Admin Console should then appear.

Hot Deployment
--------------
Hot Deployment is accomplished by using WebSphere's "Monitored Directory Deployment" feature (see official documentation here: http://www-01.ibm.com/support/knowledgecenter/SS7JFU_8.5.5/com.ibm.websphere.express.doc/ae/urun_app_global_deployment.html?lang=en). In order to deploy an EAR just put it in the following directory: `app-root/data/profile/monitoredDeployableApps/servers/server1`.

In addition to this you can also Jenkins as a build server for your application. Just login to your OpenShift Console, select your WebSphere application and click `Enable Jenkins`. This will create a new Jenkins job for your application that will be triggered after each GIT push to your OpenShift instance.


C. Reference Information
========================

WebSphere specific
------------------
* Command reference "manageprofiles.sh" - http://pic.dhe.ibm.com/infocenter/wasinfo/v8r5/topic/com.ibm.websphere.express.doc/ae/rxml_manageprofiles.html
* Disable Security HTTPS for Web App - http://www-01.ibm.com/support/docview.wss?uid=swg21408274
* Configure WebSphere to bind to specific IP - http://www-01.ibm.com/support/knowledgecenter/SSAW57_8.5.5/com.ibm.websphere.nd.doc/ae/trun_multiplenic.html?lang=en
* WebSphere Global Deployment Settings - http://www-01.ibm.com/support/knowledgecenter/SS7JFU_8.5.5/com.ibm.websphere.express.doc/ae/urun_app_global_deployment.html?lang=en
* WebSphere Auto Deployment - http://www.webspheretools.com/sites/webspheretools.nsf/docs/WebSphere%208%20Auto%20Deploy
* File Permissions for non-admin install - http://www-01.ibm.com/support/knowledgecenter/SS7JFU_8.5.5/com.ibm.websphere.express.doc/ae/tpro_nonrootpro.html?lang=en


OpenShift specific
------------------
* Cartridge Developers Guide - http://openshift.github.io/documentation/oo_cartridge_developers_guide.html
* How to expose more than one public port - https://github.com/sosiouxme/diy-extra-port-cartridge/tree/ssl-hack and https://www.openshift.com/content/at-least-one-port-for-external-use-excluding-8080-please
* WebSphere Liberty Cartridge - https://github.com/WASdev/cloud.openshift.cartridge.wlp

