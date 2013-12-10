from axiom import attributes, item
from axiom.errors import ItemNotFound
from OpenSSL.SSL import Context, VERIFY_PEER, SSLv23_METHOD
from OpenSSL.SSL import OP_SINGLE_DH_USE, OP_NO_SSLv2, OP_NO_SSLv3
from twisted.python import log


class User(item.Item):
    """
    A user.
    """
    email = attributes.bytes(allowNone=False) # TODO: index
    digest = attributes.bytes()



class UserMixin(object):
    _user = None

    @property
    def user(self):
        """The current user.

        This property is cached in the ``_user`` attribute.
        """
        if self._user is not None:
            return self._user

        cert = self.transport.getPeerCertificate()
        email = cert.get_subject().CN.encode("utf-8")
        self._user = user = self.store.findUnique(User, User.email == email)
        return user



class ContextFactory(object):
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
        ctx.set_options(OP_SINGLE_DH_USE|OP_NO_SSLv2|OP_NO_SSLv3)
        ctx.set_verify(VERIFY_PEER, self._verify)
        return ctx


    def _verify(self, connection, cert, errorNumber, errorDepth, returnCode):
        """Verify a certificate.

        """
        try:
            email = cert.get_subject().CN.encode("utf-8")
            user = self.store.findUnique(User, User.email == email)
        except ItemNotFound:
            log.msg("Connection attempt by CN {0!r}, but no user with that "
                    "e-mail address was found".format(email))
            return False

        digest = cert.digest("sha512")
        if user.digest is None:
            user.digest = digest
            log.msg("First connection by {!0r}, stored digest: "
                    "{1}".format(email, digest))
            return True
        elif user.digest == digest:
            log.msg("Successful connection by {0!r}".format(email))
            return True
        else:
            log.msg("Failed connection by {0!r}; cert digest was {}, "
                    "expecting {}".format(email, digest, user.digest))
            return False
