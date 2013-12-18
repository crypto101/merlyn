from axiom import attributes, item
from axiom.errors import ItemNotFound
from twisted.python.reflect import namedAny


class _PersistedFactory(item.Item):
    identifier = attributes.bytes(indexed=True)
    name = attributes.bytes()

    def dereference(self):
        return namedAny(self.name)



class FactoryDict(object):
    """A collection of multiplexable factories.

    This object is read-only.

    """
    def __init__(self, store):
        self.store = store


    def __getitem__(self, key):
        PF = _PersistedFactory
        try:
            persistedFactory = self.store.findUnique(PF, PF.identifier == key)
        except ItemNotFound:
            raise KeyError(key)

        return persistedFactory.dereference()



def addToStore(store, identifier, name):
    """Adds a persisted factory with given identifier and object name to
    the given store.

    This is intended to be partially applied.

    The only difference between this and ``PeristedFactory`` itself is
    that you have to pass a store to ``PersistedFactory`` as the
    ``store`` keyword argument, whereas you can pass it to this
    function positionally.

    """
    return _PersistedFactory(store=store, identifier=identifier, name=name)
