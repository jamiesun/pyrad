import socket, asyncoro
from pyrad import dictionary
from pyrad import host
from  pyrad.packet import AccessRequest
import time

class AuthTestClient(host.Host):
    def __init__(self, server, authport=1812, acctport=1813,
        secret="secret", dict=dictionary.Dictionary("dictionary")):
        host.Host.__init__(self, dict=dict)
        self.server = server
        self.authport = authport
        self.acctport = acctport
        self.secret = secret
        self.total = 5000
        self.sock = asyncoro.AsynCoroSocket(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,1024*10*20)
        self.sock.settimeout(10)
        asyncoro.Coro(self.send)
        asyncoro.Coro(self.recv)

    def recv(self, coro=None):
        startrecv = time.time()
        
        reply = 0
        while 1:
            try:
                msg, addr = yield self.sock.recvfrom(8192)
                reply += 1
                lasttime = time.time()
                #print('Received "%s" from %s:%s' % ("msg", addr[0], addr[1]))
            except socket.timeout:
                break
            #print('Received "%s" from %s:%s' % (msg, addr[0], addr[1]))

        times = lasttime - startrecv
        percount = reply /times
        print ("reply:%s"%reply)
        print ("reply per second:%s"%percount)
        self.sock.close()

    def send(self, coro=None):
        startsend = time.time()
        lastsend = time.time()
        for i in xrange(self.total):
            if time.time()-lastsend > 5:
                lastsend = time.time()
                sendtimes = lastsend - startsend
                print ("sends per second:%s"%(self.total/sendtimes))                
                #yield coro.suspend(timeout=0.1)
                #print "send suspend 100 ms"

            req=self.CreateAuthPacket(code=AccessRequest,
                User_Name="test01",secret=self.secret)
            req["User-Password"] = req.PwCrypt("888888")
            req["NAS-IP-Address"]     = "198.168.8.139"     
            yield self.sock.sendto(req.RequestPacket(),(self.server,self.authport)) 

if __name__ == '__main__':
    AuthTestClient("198.168.8.139",secret="secret")
        