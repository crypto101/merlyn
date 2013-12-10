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
    digest = attributes.bytes()



class Locator(CommandLocator):
    _user = None

    @property
    def user(self):
        """The current user.

        This property is cached in the ``_user`` attribute.
        """
        if self._user is not None:
            return self._user

        try:
            user = self.store.findUnique(User, User.digest == self._digest)
        except ItemNotFound:
            return None

        self._user = user
        return user


    @property
    def _digest(self):
        """The SHA-512 digest of the current client certificate.

        """
        return self.transport.getPeerCertificate().digest("sha512")


    @Register.responder
    def register(self, email):
        if self.user is not None:
            raise AlreadyRegistered()

        try:
            withThisEmail = User.email == email
            user = self.store.findUnique(User, withThisEmail)
        except ItemNotFound:
            raise BadEmailAddress()

        if user.digest is not None:
            raise AlreadyRegistered()

        user.digest = self._digest()
        self._user = user
        return {}



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
