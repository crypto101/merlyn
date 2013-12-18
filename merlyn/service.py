from axiom import store
from merlyn import auth, exercise, manhole
from twisted.application import service
from twisted import plugin
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.protocols.amp import AMP
from twisted.python import usage
from zope import interface


class AMP(AMP, exercise.Locator, auth.UserMixin):
    """
    The merlyn AMP protocol.
    """
    @property
    def store(self):
        return self.factory.store


    def connectionMade(self):
        """Keep a reference to the protocol on the factory.

        Unfortunately, we can't add the protocol by TLS certificate
        fingerprint, because the TLS handshake won't have completed
        yet, so ``self.transport.getPeerCertificate()`` is still
        ``None``.

        """
        self.factory.protocols.add(self)
        super(AMP, self).connectionMade()


    def connectionLost(self, reason):
        """Lose the reference to the protocol on the factory.

        """
        self.factory.protocols.remove(self)
        super(AMP, self).connectionLost(reason)



class AMPFactory(ServerFactory):
    protocol = AMP

    def __init__(self, store):
        self.store = store
        self.protocols = set()



class Options(usage.Options):
    """
    The options for starting a service.
    """
    optParameters = [
        ["store", "s", None, "Path to the store (mandatory)", store.Store]
    ]

    def postOptions(self):
        """Verify that a store was passed.

        """
        if self["store"] is None:
            raise usage.UsageError("Passing a root store is mandatory.")



class Service(service.Service):
    def __init__(self, store, reactor=reactor):
        self.store = store
        self.reactor = reactor


    def startService(self):
        factory = AMPFactory(store)
        ctxFactory = auth.ContextFactory(self.store)
        self.reactor.listenSSL(4430, factory, ctxFactory)

        manholeFactory = manhole.makeFactory(self.store, factory)
        self.reactor.listenTCP(8888, manholeFactory, interface="localhost")



@interface.implementer(plugin.IPlugin, service.IServiceMaker)
class ServiceMaker(object):
    """
    Makes a merlyn service from the command line.
    """
    tapname = "merlyn"
    description = "Exercise server"
    options = Options

    def makeService(self, options):
        return Service(options["store"])
