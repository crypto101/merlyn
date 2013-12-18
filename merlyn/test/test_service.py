from axiom.store import Store
from merlyn import service
from twisted.internet.protocol import connectionDone
from twisted.test.proto_helpers import StringTransport
from twisted.trial.unittest import SynchronousTestCase


class AMPTests(SynchronousTestCase):
    """Test cases for the AMP protocol class and its factory.

    """
    def setUp(self):
        self.store = Store()
        self.factory = service.AMPFactory(self.store)


    def test_keepReference(self):
        """The protocol registers itself to its factory when a connection is
        made. The reference is removed when the connection is lost.

        """
        self.assertEqual(self.factory.protocols, set([]))

        proto = self.factory.buildProtocol(None)
        proto.makeConnection(StringTransport())
        proto.connectionMade()
        self.assertEqual(self.factory.protocols, set([proto]))

        proto.connectionLost(connectionDone)
        self.assertEqual(self.factory.protocols, set([]))


    def test_factoryHasStore(self):
        """The factory exposes its store as the ``store`` attribute.

        """
        self.assertIdentical(self.factory.store, self.store)


    def test_protocolsHaveStore(self):
        """Protocols have a reference to a store, which is the factory's store.

        """
        proto = self.factory.buildProtocol(None)
        self.assertIdentical(proto.store, self.store)



class ServiceMakerTests(SynchronousTestCase):
    def test_options(self):
        """The service maker uses the merlyn Options class.

        """
        self.assertIdentical(service.ServiceMaker.options, service.Options)


    def test_tapname(self):
        """The service maker uses the tapname ``merlyn``.

        """
        self.assertIdentical(service.ServiceMaker.tapname, b"merlyn")


    def test_makeService(self):
        """The service maker grabs the store from the options, and passes it
        to ``service.Service``.

        """
        maker = service.ServiceMaker()
        store = Store()
        svc = maker.makeService({"store": store})
        self.assertTrue(isinstance(svc, service.Service))
        self.assertIdentical(svc.store, store)
