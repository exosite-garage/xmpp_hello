## xmmp_hello.py
## Tested with python 2.6.5
##
## Copyright (c) 2010, Exosite LLC
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##    * Redistributions of source code must retain the above copyright notice,
##      this list of conditions and the following disclaimer.
##    * Redistributions in binary form must reproduce the above copyright 
##      notice, this list of conditions and the following disclaimer in the
##      documentation and/or other materials provided with the distribution.
##    * Neither the name of Exosite LLC nor the names of its contributors may
##      be used to endorse or promote products derived from this software 
##      without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
## ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
## LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
## CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
## SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
## INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
## CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
## ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
## POSSIBILITY OF SUCH DAMAGE.

'''Hello World program using the Exosite XMPP API'''

import sys
import time
import xmpp
import ConfigParser

#===============================================================================
def main():
#===============================================================================
  ## setup our connection and data source variables
  connection = {'exosite_bot':'','user_id':'','password':'','cik':''}
  datasources = {'hello_world':''}

  ## read connection and data source values from config file    
  connection, datasources = getconfiguration(connection, datasources) 

  exompp = Exompp(connection)
  ## try to connect to Exosite
  if -1 == exompp.connect():
    print "Could not connect - check your server settings"
    return -1

  ##setup data source names and resource numbers in your portal
  for k, v in datasources.iteritems():
    if -1 == exompp.createdatasource(k,datasources[k]):
      print "Problem with data source - check name and resource # pairing"
      return -1

  ## send hello_world to your portal
  if -1 == exompp.write(datasources['hello_world'], 'Hello World!'):
    print "Problem with writing data source, check write string and try again."
    return -1

  print "Sent \"Hello World!\" to your Portal!  View at exosite.com"

#===============================================================================
def getconfiguration(connection, datasources):
#===============================================================================
  config = ConfigParser.RawConfigParser()
  config.read('options.cfg')
  print "\n"
  print "======================"
  print "Connection Settings:"
  print "======================"
  for k, v in connection.iteritems():
    try:
      connection[k] = config.get('Connection',k)
      print "%s: %s" % (k,connection[k])
    except:
      print "\"%s\" not found in config file." % k
  print "======================"
  print "\n"
  print "======================"
  print "Data Source Settings:"
  print "======================"
  for k, v in datasources.iteritems():
    try:
      datasources[k] = config.get('DataSources',k)
      print "%s: %s" % (k,datasources[k])
    except:
      print "\"%s\" not found in config file." % k
  print "======================"
  print "\n"
  return connection, datasources

#===============================================================================
class Exompp():
#===============================================================================
#-------------------------------------------------------------------------------
  def __init__(self, connection):
    self.connection = connection
    self.duplicate = False
    self.dsname = ''
    self.dsresource = ''

#-------------------------------------------------------------------------------
  def connect (self):
    try:
      jid = xmpp.protocol.JID(self.connection['user_id'])
    except:
      print "Unable to establish XMPP connection"
      return -1
    cl = xmpp.Client(jid.getDomain(), debug=0)
    self.messenger = Messenger(cl)
    con = cl.connect()
    try:
      auth = cl.auth(jid.getNode(), self.connection['password'])
    except:
      print "Authentication failed"
      return -1
    if not auth:
      print "Authentication failed"
      return -1
    cl.RegisterHandler('message', self.messenger.message_handler)
    msg = xmpp.protocol.Message(to=self.connection['exosite_bot'],
                                body='setcik %s\n' % self.connection['cik'],
                                typ='chat')
    self.messenger.send(msg)
    if self.messenger.wait() == -1:
      print "Response error or timed out"
      return -1

#-------------------------------------------------------------------------------        
  def createdatasource (self, name, resource):
    self.dsname = name  
    self.dsresource = resource    
    msg = xmpp.protocol.Message(to=self.connection['exosite_bot'],
                                body='dslist full',
                                typ='chat')

    self.messenger.send(msg, self.dslistcallback)
    if self.messenger.wait() == -1:
      print "Response error or timed out"
      return -1
    
    if self.duplicate:
      print "Data source %s is already setup, continuing..." % name
      self.duplicate = False
    else:
      msg = xmpp.protocol.Message(to=self.connection['exosite_bot'],
                                  body='dscreate %s %s na 0' % (name, resource),
                                  typ='chat')

      self.messenger.send(msg, self.cdscallback)
      if self.messenger.wait() == -1:
        print "Response error or timed out"
        return -1

#-------------------------------------------------------------------------------
  def write (self, resource, data):
    msg = xmpp.protocol.Message(to=self.connection['exosite_bot'],
                                body='write %s %s' % (resource, data),
                                typ='chat')
    self.messenger.send(msg, self.stdcallback)
    if self.messenger.wait() == -1:
      print "Response error or timed out"
      return -1

#-------------------------------------------------------------------------------
  def read (self, resource):
    msg = xmpp.protocol.Message(to=self.connection['exosite_bot'],
                                body='read %s\n' % resource,
                                typ='chat')
    self.messenger.send(msg, self.stdcallback)
    if self.messenger.wait() == -1:
      print "Response error or timed out"
      return -1

#-------------------------------------------------------------------------------
  def stdcallback (self, response):
    print(response)

#-------------------------------------------------------------------------------
  def cdscallback (self, response):
    if response.find("error") != -1:
      print "CreateDataSource Error: response: %s" % response
      return -1

#-------------------------------------------------------------------------------
  def dslistcallback (self, response):
    start = response.find(self.dsname)    
    if start != -1:
      self.duplicate = True
      start = response.find(',',start) + 1
      end = response.find(',',start)
      if self.dsresource != response[start:end]:
        print "Error: Duplicate resource name, but resource # does not match."        
        return -1

#===============================================================================
class Messenger(object):
#===============================================================================
#-------------------------------------------------------------------------------
  def __init__(self, client):
    self.wait_for_response = False
    self.callback = None
    self.client = client
    self.start = 0

#-------------------------------------------------------------------------------
  def wait(self):
    self.start = time.clock()
    while self.wait_for_response:
      if time.clock() - self.start > 10:
        self.wait_for_response = False 
        return -1
      if not self.client.Process(1):
        print 'disconnected'
        break

#-------------------------------------------------------------------------------
  def message_handler(self, con, event):
    response = event.getBody()
    if self.callback:
      if -1 == self.callback(response):
        print "WARNING: XMPP response: %s" % response
        self.start = time.clock() - 11
      else:
        self.wait_for_response = False
    else:
      if response.find("ok") == -1:
        print "ERROR: XMPP response: %s" % response
        self.start = time.clock() - 11
      else:
        self.wait_for_response = False

#-------------------------------------------------------------------------------
  def send(self, message, callback=None):
    self.wait_for_response = True
    self.callback = callback
    self.client.send(message)

#===============================================================================        
if __name__ == '__main__':
  sys.exit(main())

