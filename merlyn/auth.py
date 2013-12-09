from axiom import attributes, item
from axiom.errors import ItemNotFound
from clarent.auth import Register
from clarent.auth import BadEmailAddress, AlreadyRegistered, NotRegistered
from functools import wraps
from twisted.protocols.amp import CommandLocator


class User(item.Item):
    """
    A user.
    """
    email = attributes.bytes(allowNone=False)
    fingerprint = attributes.bytes()



class Locator(CommandLocator):
    _user = None

    @property
    def user(self):
        if self._user is not None:
            return self._user

        cert = self.transport.getPeerCertificate()
        if cert is None:
            return None # TODO: Remove this.

        withThisFingerprint = User.fingerprint == cert

        try:
            user = self.store.findUnique(User, withThisFingerprint)
        except ItemNotFound:
            return None

        self._user = user
        return user


    @Register.responder
    def register(self, email):
        if self.user is not None:
            raise AlreadyRegistered()

        import pudb; pudb.set_trace()

        try:
            withThisEmail = User.email == email
            user = self.store.findUnique(User, withThisEmail)
        except ItemNotFound:
            raise BadEmailAddress()

        if user.fingerprint:
            raise AlreadyRegistered()

        cert = self.transport.getPeerCertificate()



def loginRequired(m):
    """Decorates a responder method, so that it can only be used while
    logged in.

    """
    @wraps(m)
    def decorated(self, *a, **kw):
        if self.user is not None:
            return m(self, *a, **kw)
        else:
            raise NotRegistered()
    return decorated
