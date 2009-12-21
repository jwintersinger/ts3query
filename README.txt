========
Ts3Query
========
Version: 0.1
License: Public domain
Author: Micand (but you may call me Jeff)


=====
About
=====
Ts3Query is a simple Python client for Teamspeak 3's ServerQuery system. Out of
the box, it only displays a list of clients and channels, but given its solid
support for the underlying ServerQuery protocol, it can easily be expanded to
perform any of the operations allowed by ServerQuery.

Ts3Query can be used as a standalone Web application, a Python library, or a
command-line application. The command-line interface can display human-readable
output or spit out JSON, allowing usage in non-Python programming environments.


============
Requirements
============
Only Python 2.5 or higher is needed. Ts3Query is not compatible with Python 3.


=====
Usage
=====
For any usage mode other than stand-alone Web app, only the file ts3query.py is
necessary -- all others may be discarded.

-------------------
Stand-alone Web app
-------------------
Ts3Query can function as a simple web.py application. (The latest version of
web.py as of this writing, 0.33, is bundled with Ts3Query, but you can upgrade
to more recent versions at your discretion.) Simply run "python ts3web.py" to
bring up the Web interface on port 8080. Alternatively, Ts3Query can be
deployed on any existing Web server that supports WSGI as per
http://webpy.org/install.

----------------------
Command-line interface
----------------------
Run "python ts3query.py [-p PORT] server_address" to print human-readable
output. The -p option is necessary only if the Teamspeak server does not reside
on the default port. Pass the -h option to print all possible options and
arguments.

Examples:
  * python ts3query.py voice.teamspeak.com
  * python ts3query.py ts.example.com -p 1337

-------------------------------
JSON via command-line interface
-------------------------------
Pass the -j option to ts3query.py to output JSON (e.g., python ts3query.py -j
voice.teamspeak.com). This potentially allows for usage from non-Python
programming environments.

--------------
Python library
--------------
The TsQuery class implements a low-level interface to ServerQuery, while
TsConverser provides a higher-level one. TsQuery allows you to run any command
provided by ServerQuery, while TsConverser supports only those defined by the
programmer, albeit through a more genteel interface.

TsQuery usage:
  tsq = TsQuery('voice.teamspeak.com') # Can pass port number as optional second argument.
  # No parameters or options
  print tsq.query('clientlist')
  # Just parameters, no options
  print tsq.query('login', {'client_login_name': 'serveradmin', 'client_login_password': 'pass'})
  # Just options, no parameters
  print tsq.query('clientlist', options=('away',))
  # Options and parameters
  print tsq.query('clientdbfind', {'pattern': 'Jeff'}, ('away',))

TsConverser usage:
  tsc = TsConverser('voice.teamspeak.com') # Can pass port number as optional second argument.
  # Whereas tsq.query('clientlist') lists only channels, this will list
  # channels along with a list of clients in each, omitting channels that are
  # empty. It's a happier interface!
  print tsc.list_populated_channels()

