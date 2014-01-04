from axiom import store
from merlyn import auth, exercise, manhole, multiplexing
from twisted.application import service
from twisted import plugin
from twisted.internet import protocol, reactor
from twisted.protocols.amp import AMP
from twisted.python import usage
from txampext.multiplexing import MultiplexingCommandLocator
from zope import interface


class Protocol(AMP, exercise.Locator, auth.UserMixin, MultiplexingCommandLocator):
    """
    The merlyn AMP protocol.
    """
    def __init__(self):
        MultiplexingCommandLocator.__init__(self)
        AMP.__init__(self)


    @property
    def store(self):
        return self.factory.store


    def connectionMade(self):
        """Keep a reference to the protocol on the factory, and uses the
        factory's store to find multiplexed connection factories.

        Unfortunately, we can't add the protocol by TLS certificate
        fingerprint, because the TLS handshake won't have completed
        yet, so ``self.transport.getPeerCertificate()`` is still
        ``None``.

        """
        self.factory.protocols.add(self)
        self._factories = multiplexing.FactoryDict(self.store)
        super(AMP, self).connectionMade()


    def connectionLost(self, reason):
        """Lose the reference to the protocol on the factory.

        """
        self.factory.protocols.remove(self)
        super(AMP, self).connectionLost(reason)



class Factory(protocol.ServerFactory):
    protocol = Protocol

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
        factory = Factory(self.store)
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
