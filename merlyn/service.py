from axiom import store
from merlyn import auth, exercise
from OpenSSL.SSL import Context, VERIFY_PEER, SSLv23_METHOD
from OpenSSL.SSL import OP_SINGLE_DH_USE, OP_NO_SSLv2, OP_NO_SSLv3
from twisted.application import service
from twisted import plugin
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.protocols.amp import AMP
from twisted.python import usage
from zope import interface


class AMP(AMP, exercise.Locator, auth.Locator):
    """
    The merlyn AMP protocol.
    """
    @property
    def store(self):
        return self.factory.store



class Options(usage.Options):
    """
    The options for starting a service.
    """
    optParameters = [
        ["store", "s", None, "Path to root store (mandatory)", store.Store]
    ]

    def postOptions(self):
        """Verify that a store was passed.

        """
        if self["store"] is None:
            raise usage.UsageError("Passing a root store is mandatory.")



class Service(service.Service):
    def __init__(self, store):
        self.store = store


    def startService(self):
        factory = ServerFactory.forProtocol(AMP)
        factory.store = self.store
        reactor.listenSSL(4430, factory, ContextFactory())



class ContextFactory(object):
    def getContext(self):
        """Creates a context.

        This will make contexts using ``SSLv23_METHOD``. This is
        because OpenSSL thought it would be a good idea to have
        ``TLSv1_METHOD`` mean "only use TLSv1.0" -- specifically, it
        disables TLSv1.2. Since we don't want to use SSLv2 and v3, we
        set OP_NO_SSLv2|OP_NO_SSLv3. Additionally, we set
        OP_SINGLE_DH_USE.

        """
        ctx = Context(SSLv23_METHOD)
        ctx.use_certificate_file("cert.pem")
        ctx.use_privatekey_file("key.pem")
        ctx.set_options(OP_SINGLE_DH_USE|OP_NO_SSLv2|OP_NO_SSLv3)
        ctx.set_verify(VERIFY_PEER, _verify)
        return ctx



def _verify(connection, x509, errorNumber, errorDepth, returnCode):
    """Always pretend the certificate verified.

    """
    return True



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
