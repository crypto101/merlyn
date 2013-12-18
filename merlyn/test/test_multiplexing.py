from axiom.store import Store
from functools import partial
from merlyn.multiplexing import addToStore, FactoryDict, _PersistedFactory
from twisted.trial.unittest import SynchronousTestCase


theFactory = object()
theNameOfTheFactory = "merlyn.test.test_multiplexing.theFactory"


class FactoryDictTests(SynchronousTestCase):
    """FactoryDicts are like dicts of names and identifiers except in an
    axiom store.

    """
    def setUp(self):
        self.store = Store()
        self.factoryDict = FactoryDict(self.store)
        _PersistedFactory(store=self.store,
                          identifier="identifier",
                          name=theNameOfTheFactory)


    def test_get(self):
        """FactoryDicts supply factories by identifiers.

        """
        self.assertIdentical(self.factoryDict["identifier"], theFactory)


    def test_getMissing(self):
        """FactoryDicts raise KeyError when there is no factory with the given
        identifier.

        """
        self.assertRaises(KeyError, lambda: self.factoryDict["BOGUS"])


    def test_addToStore(self):
        """The addToStore function adds a persisted factory to a store.

        """
        addThisToStore = partial(addToStore,
                                 identifier="otherIdentifier",
                                 name=theNameOfTheFactory)

        self.assertRaises(KeyError, lambda: self.factoryDict["otherIdentifier"])
        addThisToStore(self.store)
        self.assertIdentical(self.factoryDict["otherIdentifier"], theFactory)
