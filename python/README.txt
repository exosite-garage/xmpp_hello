========================================
About
========================================
xmpp_hello.py is a simple python script that demonstrates how to send data to
the Exosite over XMPP.

License is BSD, Copyright 2010, Exosite LLC

Built/tested with Python 2.6.5

========================================
Quick Start
========================================
****************************************
1) install python
****************************************
http://www.python.org/download/
http://www.python.org/download/releases/2.6.5/
http://www.python.org/ftp/python/2.6.5/python-2.6.5.msi

****************************************
2) install xmpppy
****************************************
http://xmpppy.sourceforge.net/
http://sourceforge.net/projects/xmpppy/
http://sourceforge.net/projects/xmpppy/files/xmpppy/0.4.0/xmpppy-0.4.0.win32.exe/download

If running Debian Linux (or Ubuntu), you can > apt-get install python-xmpp

****************************************
3) test it out
****************************************
get python script "xmpp_hello.py" and "options.cfg"
--) update the default credentials in options.cfg to use your xmpp login and 
    device CIK
--) run the script (> python xmpp_hello.py)
--) verify the app connects, creates a datasource and sends data (no errors 
    should be generated)
--) log into exosite.com and verify the data source is created and that 
    data was generated

****************************************
4) tweak it
****************************************
--) add a 'print' command or something 
--) play around, use it, extend it!
