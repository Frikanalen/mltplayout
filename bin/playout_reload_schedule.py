from autobahn.websocket import WebSocketClientFactory
from autobahn.websocket import WebSocketClientProtocol
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint


class SendCommandProtocol(WebSocketClientProtocol):
    def onOpen(self):
        print "Sent: reload-schedule"
        x = self.sendMessage("reload-schedule: True")
        print x
        # jesus christ. sendMessage should support deferred
        reactor.callLater(1.0, reactor.stop)

    def onMessage(self, msg, binary):
        print "Reply: " + msg


def failed(reason):
    print "failed: %s" % reason


def playout_reload_schedule(host, port):
    print("Connecting to ws://%s:%s" % (host, port))
    factory = WebSocketClientFactory("ws://%s:%s" % (host, port))
    factory.protocol = SendCommandProtocol
    point = TCP4ClientEndpoint(reactor, host, port)
    d = point.connect(factory)
    d.addErrback(failed)
    return d


if __name__ == '__main__':
    import sys
    if not (len(sys.argv) == 3):
        print("usage: playout_reload_schedule hostname port")
        sys.exit()
    host = sys.argv[1]
    port = sys.argv[2]
    print host, port
    playout_reload_schedule(host, int(port))
    reactor.run()
