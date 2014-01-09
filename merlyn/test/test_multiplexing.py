from axiom.store import Store
from functools import partial
from merlyn.multiplexing import addToStore, FactoryDict
from twisted.trial.unittest import SynchronousTestCase


class Factory(object):
    def __init__(self, store):
        self.store = store



prefix = "merlyn.test.test_multiplexing."
name = prefix + "Factory"



class OtherFactory(Factory):
    """Another factory.

    """



otherName = prefix + "OtherFactory"



class FactoryDictTests(SynchronousTestCase):
    """FactoryDicts are like dicts of names and identifiers except in an
    axiom store.

    """
    def setUp(self):
        self.store = Store()
        self.factoryDict = FactoryDict(self.store)
        addToStore(self.store, "test", name)


    def test_get(self):
        """FactoryDicts supply factories by identifiers. These factories are
        instantiated with the store.

        """
        self.checkFactory(self.factoryDict["test"])


    def checkFactory(self, factory, cls=Factory):
        """Checks the given factory. It must be an instance of the given class
        (default: Factory), as well as have the test store as the
        ``store`` attribute.

        """
        self.assertTrue(isinstance(factory, cls))
        self.assertIdentical(factory.store, self.store)


    def test_getMissing(self):
        """FactoryDicts raise KeyError when there is no factory with the given
        identifier.

        """
        self.assertRaises(KeyError, lambda: self.factoryDict["BOGUS"])


    def test_updateInStore(self):
        """The addToStore function will update a peristed factory's name, if a
        persisted factory with the passed identifier already exists.

        """
        addToStore(self.store, "test", otherName)
        self.checkFactory(self.factoryDict["test"], cls=OtherFactory)
