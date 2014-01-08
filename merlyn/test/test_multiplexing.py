from axiom.store import Store
from functools import partial
from merlyn.multiplexing import addToStore, FactoryDict, _PersistedFactory
from twisted.trial.unittest import SynchronousTestCase


theFactory = object()
theNewFactory = object()

prefix = "merlyn.test.test_multiplexing."
theNameOfTheFactory = prefix + "theFactory"
theNameOfTheNewFactory = prefix + "theNewFactory"


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


    def test_updateInStore(self):
        """The addToStore function will update a peristed factory's name, if a
        persisted factory with the passed identifier already exists.

        """
        addName = partial(addToStore, self.store, "identifier")
        def checkFactory(expected):
            self.assertIdentical(self.factoryDict["identifier"], expected)

        addName(theNameOfTheFactory)
        checkFactory(theFactory)

        addName(theNameOfTheNewFactory)
        checkFactory(theNewFactory)
