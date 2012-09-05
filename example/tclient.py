#!/usr/bin/env python
#coding:utf-8
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.python import log
import sys,socket
from pyrad import dictionary
from pyrad import host
import pyrad
import time

class RadiusTestClient(host.Host, protocol.DatagramProtocol):
    def __init__(self, server, authport=1812, acctport=1813,
        secret="secret", dict=dictionary.Dictionary("dictionary")):
        host.Host.__init__(self, dict=dict)
        self.server = server
        self.authport = authport
        self.acctport = acctport
        self.secret = secret
        self.reply = 0
        
    def startProtocol(self):
        self.transport.socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,1024*10*20)
        self.transport.connect(self.server, self.authport)
        self.sendAuth()
        reactor.callLater(60,self.done)

    def done(self):
        times = self.lasttime - self.starttime
        percount = self.reply /times
        log.msg("reply:%s"%self.reply)
        log.msg("reply per second:%s"%percount)
        reactor.stop()

    def sendAuth(self):
        self.starttime = time.time()
        for i in xrange(1000):
            req=self.CreateAuthPacket(code=pyrad.packet.AccessRequest,
                User_Name="test01",secret=self.secret)
            req["User-Password"] = req.PwCrypt("888888")
            req["NAS-IP-Address"]     = "198.168.8.139"     
            self.transport.write(req.RequestPacket())    
        sendtimes = time.time() - self.starttime
        log.msg("sends per second:%s"%(1000/sendtimes))

    def datagramReceived(self, datagram, (host, port)):
        self.reply += 1
        self.lasttime = time.time()

def main():
    log.startLogging(sys.stdout, 0)
    protocol = RadiusTestClient("198.168.8.8",secret="secret")
    reactor.listenUDP(0, protocol)
    reactor.run()

if __name__ == '__main__':
    main()