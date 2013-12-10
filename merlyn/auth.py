from axiom import attributes, item
from axiom.errors import ItemNotFound
from clarent.auth import Register
from clarent.auth import BadEmailAddress, AlreadyRegistered, NotRegistered
from functools import wraps
from OpenSSL.SSL import Context, VERIFY_PEER, SSLv23_METHOD
from OpenSSL.SSL import OP_SINGLE_DH_USE, OP_NO_SSLv2, OP_NO_SSLv3
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
        """Registers the user, identified with the given email address, to
        the current connection's certificate digest.

        """
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
