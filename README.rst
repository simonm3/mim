MIM Usage
=========
Description
-----------

This is a man-in-the-middle proxy server. It fires signals that make it easy for plugins to read and manipulate requests and responses.

Scripts (run with -h to see usage and options)
----------------------------------------------

* proxy.py:       entry point to start the proxyserver with plugins
* users.py: 	list users on the network so you can select a target
* arp.py: 	 arp poison
* fakeAP.py:	create fake access point [https://github.com/DanMcInerney/fakeAP]
* fwreset(bash): 	reset iptables. Usually no need to call directly.

Options to send requests to the proxy
-------------------------------------

i. Redirect browser

	- Set browser proxy settings to point to ip address of proxy PC port 10000
	- ./proxy.py

ii. Run arp attack

	- ./proxy.py [NOTE: run first else target will have loss of service]
	- ./users.py to see available machines to target on the local network
	- sudo ./arp.py -t <ip address> to initiate arp attack on a target ip

iii. Run fake access point
	
	- sudo ./fakeAP.py
	- connect to Free Wifi from target pc
	- ./proxy.py [NOTE: run after fakeAP to set firewall settings]

Plugin options for proxy.py
---------------------------

      --auth         Log userids/passwords
      --beef         Inject beef hook (browser exploitation framework)
      --cats         Replace images with cats
      --favicon      Send lock favicon
      --inject       Inject data/injection.html
      --kill         Kill session on first visit to domain
      --requests     Log requests
      --sslstrip     Replace https with http then proxy links via https
      --upsidedown   Show images upsidedown

Where does it work
------------------

* Tested via usage on a range of websites using proxy settings, arp attack and fakeAP
* It should never block and has a timeout on web requests

Where does it not work
----------------------

* Some security software prevents arp attacks
* HttpsEverywhere (chrome extension) prevents interception
* Some websites enforce https

-----

MIM Structure
=============

Built using "twisted" and follows this chain:

* proxy1 (runs proxy.py with selected options)

   => Proxy.py

* proxyserver [listens for connections]

   => ProxyFactory(http.HTTPFactory)

   => Proxy(http.HTTPChannel)

   => Request(http.Request)

* proxyclient [creates connections to web]

   => ProxyClientFactory(proxy.ProxyClientFactory)

   => ProxyClient(proxy.ProxyClient, TimeoutMixin)

   => internet

Uses pydispatch2 (extended pydispatch) to manage signals

* proxyclient and proxyserver send signals
* plugins listen for signals

Plugins
-------

To create a plugin called "test":

* Create a module file "plugins/test.py".
* Use decorators e.g. @on(requestReceived) to link functions to the events fired by the proxy. The decorators are gotRequest, gotResponseTree, gotResponseText, gotResponseImage.
* Edit the docstring for proxy.py to add the option

To add a plugin to "otherplugins":

* Follow the same format as the other plugins in "otherplugins"
* Edit the docstring for proxy.py to add the option

Tools
-----

* fileserver.py: simple file server e.g. to serve images
* bash.py: wrapper for bash commands
* pydispatch2.py: decorator that connects a function to a signal

Other files
-----------

* logs.py: configuration for logs
* log.txt: log of current session. This is cleared on each run.

Requirements
------------

* pip install -r requirements.txt
* apt-get install beef-xss
