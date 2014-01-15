from axiom import attributes, item
from axiom.errors import ItemNotFound
from clarent.certificate import SecureCiphersContextFactory
from OpenSSL.SSL import Context, VERIFY_PEER, SSLv23_METHOD
from OpenSSL.SSL import OP_SINGLE_DH_USE, OP_NO_SSLv2, OP_NO_SSLv3
from twisted.python import log


class User(item.Item):
    """A user.

    """
    email = attributes.bytes(allowNone=False, indexed=True)
    digest = attributes.bytes()



class UserMixin(object):
    """A mixin that makes the user available based on the peer certificate.

    Mostly intended for command locators (that are also protocols).
    Expects a ``store`` attribute, which is the store that has all of
    the user data, as well as a ``transport`` attribute, which is the
    transport that has the peer certificate we're authenticating with.

    """
    _user = None

    @property
    def user(self):
        """The current user.

        This property is cached in the ``_user`` attribute.
        """
        if self._user is not None:
            return self._user

        cert = self.transport.getPeerCertificate()
        self._user = user = userForCert(self.store, cert)
        return user



class _TOFUContextFactory(object):
    def __init__(self, store):
        self.store = store


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
        ctx.load_tmp_dh("dhparam.pem")
        ctx.set_options(OP_SINGLE_DH_USE|OP_NO_SSLv2|OP_NO_SSLv3)
        ctx.set_verify(VERIFY_PEER, self._verify)
        return ctx


    def _verify(self, connection, cert, errorNumber, errorDepth, returnCode):
        """Verify a certificate.

        """
        try:
            user = userForCert(self.store, cert)
        except ItemNotFound:
            log.msg("Connection attempt by {0!r}, but no user with that "
                    "e-mail address was found, cert digest was {1}"
                    .format(emailForCert(cert), cert.digest("sha512")))
            return False

        digest = cert.digest("sha512")
        if user.digest is None:
            user.digest = digest
            log.msg("First connection by {0!r}, stored digest: {1}"
                    .format(user.email, digest))
            return True
        elif user.digest == digest:
            log.msg("Successful connection by {0!r}".format(user.email))
            return True
        else:
            log.msg("Failed connection by {0!r}; cert digest was {1}, "
                    "expecting {2}".format(user.email, digest, user.digest))
            return False



class ContextFactory(object):
    def __init__(self, store):
        self._wrapped = _TOFUContextFactory(store)
        self._wrapper = SecureCiphersContextFactory(self._wrapped)


    def getContext(self):
        return self._wrapper.getContext()



def emailForCert(cert):
    """Extracts the e-mail address from the X509 data in the given cert.

    """
    return cert.get_subject().emailAddress.encode("utf-8")


def userForCert(store, cert):
    """Gets the user for the given certificate.

    """
    return store.findUnique(User, User.email == emailForCert(cert))
