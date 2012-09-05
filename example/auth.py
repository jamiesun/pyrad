#!/usr/bin/python

import socket, sys
import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary


srv=Client(server="localhost",
           secret="secret",
           dict=Dictionary("dictionary"))

req=srv.CreateAuthPacket(code=pyrad.packet.AccessRequest,
                         User_Name="test01")


req["User-Password"] = req.PwCrypt("888888")
req["NAS-IP-Address"]     = "198.168.8.139"
print req.id
print req.authenticator

try:
    print "Sending authentication request"
    reply=srv.SendPacket(req)
except pyrad.client.Timeout:
    print "RADIUS server does not reply"
    sys.exit(1)
except socket.error, error:
    print "Network error: " + error[1]
    sys.exit(1)

if reply.code==pyrad.packet.AccessAccept:
    print "Access accepted"
else:
    print "Access denied"

print "Attributes returned by server:"
for i in reply.keys():
    print "%s: %s" % (i, reply[i])

