MIM Usage
=========

Description
-----------

This is a man-in-the-middle proxy server. Plugins can subscribe to events to
read and manipulate requests and responses.

A number of plugins are included. It is easy to add more based on these.

Installation
------------

* git clone https://github.com/simonm3/mim
* pip install -r requirements.txt
* If you want to use the beef framework then: apt-get install beef-xss

Scripts (run with -h to see usage and options)
----------------------------------------------

============== =================================
script			description
============== =================================
proxy.py       start the proxyserver with plugins
users.py       list users on the network so you can select a target
arp.py	    start arp poison
fakeap.sh	    create fake access point [https://github.com/DanMcInerney/fakeAP]

============== =================================

Plugin options for proxy.py
---------------------------

============== ==================================================
option			description
============== ==================================================
--auth			  Log userids/passwords
--beef            Inject beef hook (browser exploitation framework)
--cats            Replace images with cats
--favicon         Replace favicon with lock symbol
--inject          Inject data/injection.html
--kill            Kill session on first visit to domain (forces relogin)
--requests        Log requests
--sslstrip        Replace https with http then proxy links via https
--upsidedown      Turn images upsidedown

============== ==================================================

Alternative ways to send requests to the proxy
----------------------------------------------

i. Redirect browser

* proxy.py
* Set browser proxy settings to point to ip address of proxy PC port 10000

ii. Run arp attack

* proxy.py
* users.py to see available machines to target on the local network
* arp <target> to initiate arp attack on a target ip

iii. Run fake access point
	
* fakeap
* connect to Free Wifi from target pc
* proxy.py [NOTE: run after fakeAP to set firewall settings]

How to create a plugin
----------------------

* Create a module file in plugins folder based on existing plugins
* Include init function to subscribe to events and initialise
* Edit the docstring for proxy.py to add the option

Where does it work
------------------

* Tested via usage on a range of websites using proxy settings, arp attack and fakeAP
* It should never block and has a timeout on web requests

Where does it not work
----------------------

* Some security software prevents arp attacks
* Https requests typed directly in the address bar will not be intercepted
* HttpsEverywhere (chrome extension) prevents interception
* Some websites enforce https via the browser e.g. gmail, facebook
* Some websites change http links back to https after the page loads e.g. ebay
* Some websites have misformed html. Calling lxml.html.fromstring then tostring can change the appearance of the page as the parser attempts to correct problems. An alternative is to use lxml.etree instead but this causes issues with other pages and is missing functions such as rewrite_links.

-----

MIM Design
==========

Core files
----------

Built in python2.7 using "twisted.web" and follows this chain:

* proxy1 (a bash script that runs proxy.py with selected options)

   => Proxy.py

* proxyserver [listens for connections]

   => ProxyFactory(http.HTTPFactory)

   => Proxy(http.HTTPChannel)

   => Request(http.Request)

* proxyclient [creates connections to web]

   => ProxyClientFactory(proxy.ProxyClientFactory)

   => ProxyClient(proxy.ProxyClient, TimeoutMixin)

   => internet


Other files
-----------

==================== ======================================
file			     description
==================== ======================================
fileserver.py	     simple file server to serve images
bash.py		         wrapper for bash commands.
log.txt		         log of current session.
Plugins folder       subscribe to events
==================== ======================================

