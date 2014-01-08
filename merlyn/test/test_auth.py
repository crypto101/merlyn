from axiom.store import Store
from merlyn import auth
from OpenSSL.crypto import FILETYPE_PEM, load_certificate, load_privatekey
from twisted.python.log import ILogObserver, addObserver, removeObserver
from twisted.test.proto_helpers import StringTransport
from twisted.trial.unittest import SynchronousTestCase
from zope.interface import implementer
from zope.interface.verify import verifyObject


class UserTests(SynchronousTestCase):
    def test_emailIndexed(self):
        """The email attribute of the User item is indexed.

        """
        self.assertTrue(auth.User.email.indexed)



@implementer(ILogObserver)
class FakeLogObserver(object):
    def __init__(self):
        self.events = []


    def __call__(self, eventDict):
        self.events.append(eventDict)



class FakeLogObserverTests(SynchronousTestCase):
    def test_interface(self):
        """The fake log observer implements ILogObserver.

        """
        self.assertTrue(verifyObject(ILogObserver, FakeLogObserver()))



class TOFUContextFactoryTests(SynchronousTestCase):
    """Tests for TOFU/POP (Trust On First Use/Persistence of Pseudonym)
    behavior for the context factory.

    """
    def setUp(self):
        self.store = Store()
        self.user = auth.User(store=self.store, email="user@example.com")
        self.ctxFactory = auth._TOFUContextFactory(self.store)

        self.observer = FakeLogObserver()
        addObserver(self.observer)
        self.addCleanup(removeObserver, self.observer)


    def _getLogMessage(self):
        for e in self.observer.events:
            if not e.get("message"):
                continue
            return e["message"][0]


    def test_firstConnection(self):
        """First connections store the digest. Connection succeeds.

        """
        verifyResult = self.ctxFactory._verify(None, realUserCert, 0, 0, 0)
        self.assertTrue(verifyResult)
        self.assertEqual(self.user.digest, realUserCert.digest("sha512"))

        message = self._getLogMessage()
        self.assertIn("First connection", message)
        self.assertIn(self.user.email, message)
        self.assertIn(self.user.digest, message)


    def test_correctDigest(self):
        """Connection attempts with the correct digest succeed.

        """
        self.user.digest = realUserCert.digest("sha512")

        verifyResult = self.ctxFactory._verify(None, realUserCert, 0, 0, 0)
        self.assertTrue(verifyResult)

        message = self._getLogMessage()
        self.assertIn("Successful connection", message)
        self.assertIn(self.user.email, message)


    def test_noSuchEmail(self):
        """Connection attempts for unknown e-mail addresses fail.

        """
        verifyResult = self.ctxFactory._verify(None, bogusCert, 0, 0, 0)
        self.assertFalse(verifyResult)

        message = self._getLogMessage()
        self.assertIn("Connection attempt", message)
        self.assertIn("by {!r}".format(auth.emailForCert(bogusCert)), message)
        self.assertIn("digest was " + bogusCert.digest("sha512"), message)


    def test_badDigest(self):
        """Connection attempts with a bad digest fail.

        """
        self.user.digest = realUserCert.digest("sha512")

        verifyResult = self.ctxFactory._verify(None, impostorCert, 0, 0, 0)
        self.assertFalse(verifyResult)

        message = self._getLogMessage()
        self.assertIn("Failed connection", message)
        self.assertIn("digest was " + impostorCert.digest("sha512"), message)
        self.assertIn("expecting " + self.user.digest, message)



class UserMixinTests(SynchronousTestCase):
    def setUp(self):
        self.userMixin = auth.UserMixin()
        self.store = self.userMixin.store = Store()


    def test_getUser(self):
        """The user mixin gets the user using the peer certificate.

        """
        user = auth.User(store=self.store,
                         email="user@example.com",
                         digest=realUserCert.digest("sha512"))

        self.userMixin.transport = transport = StringTransport()
        transport.getPeerCertificate = lambda: realUserCert

        self.assertEqual(self.userMixin.user, user)


    def test_cache(self):
        """If the ``_user`` cache is primed, it is used.

        """
        sentinel = object()
        self.userMixin._user = sentinel
        self.assertEqual(self.userMixin.user, sentinel)



realUserKey = load_privatekey(FILETYPE_PEM, """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
""")
realUserCert = load_certificate(FILETYPE_PEM, """
-----BEGIN CERTIFICATE-----
MIIE8TCCAtkCADANBgkqhkiG9w0BAQ0FADA9MRowGAYDVQQDExFDcnlwdG8gMTAx
IENsaWVudDEfMB0GCSqGSIb3DQEJARYQdXNlckBleGFtcGxlLmNvbTAiGA8yMDEz
MTIxODAwMDAwMFoYDzIwMTgxMjE4MDAwMDAwWjA9MRowGAYDVQQDExFDcnlwdG8g
MTAxIENsaWVudDEfMB0GCSqGSIb3DQEJARYQdXNlckBleGFtcGxlLmNvbTCCAiIw
DQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKZ74kqEdCTxY0mmLN6QeMnANvgj
XL5z6RRTGbHAE8OSfh+Unfj9sWKOVz+zfCo7OkcRcLudH3j6juQV6TJbptChj94U
+4EPbpNlpGlxReRRB8AZDUmvCUx16B6eZ9kFpIf4eRuZUpI35OSM3cyWLCOy1QhZ
0vBRC+K+RDk5t9hAzSEIL9RYZk96wMO7MAFHPfOKGaxm2hgwCabfFnwhWRtJlFNY
WugEm+XbUGdqcbyeWSUXKFe73dp03kjIVCggz60KnZ8B+ue7Ok811hPFZCNKzey2
BbWgkWyPVaEVmcKLK0SYCw70TINyN22l/5UXJGMA5rDa9NtNE30gE/JKhCoXTh9M
5NzqQOyrgIwnVkGTGNQvFdoz2MLnjyH0R2DlCMVkwWpGuijTVmva9pkiwNCHGenX
X3jX+Y9q06wPYfnb5hRLSlDpKcZilFnjSyQXFM/kwYjn8zIDEVBzOgtEkAFaj1VW
WaeXVrfBl+ldsMkK4efOE22BxN5AipqWYWPk2nqEFe6Yt6ENipl9AKPeHnDKhbqi
+FhQAW9Hdb8fJMXz8idBYFPYUjK8ERPhMRq2evVRdETZJ8QWWQ0RMw/RiVZU2Vyz
sd+4vuy27SpmV3mV8Liyib65LVww2kD1Feug1mpqp41EOjZWK3RWOKJkTSEjnE/M
rY0acqHMabfGLZXxAgMBAAEwDQYJKoZIhvcNAQENBQADggIBABnlQWPzqLEqLsFb
5ykb3S3H7x8NJO8ln9xoejkKQj8YxoJbIaAThjCv3gzQbobVkDMTbpStn3AlC8fG
gQHSTfaOl+A41LFo9Y7spKjGRdFGYz7uQY6d5xgHFB+aQ0am5vuAThEp/FxTuCTA
X8JpuTPB8yLJrT7vh3446zx5fPEXhfeRw7h8QdeczgCj2CRzblqcPSplK5FbgOjE
GuefAEmeb2GU60SeLtmtXDcR28ujJrQlQgHk3xSP9Mg/YAVZ+4YnpfuiQmOWXsSA
gRTPiOR+5l47QzDnpJLPlTa+oow/mXPT58Zkimgh60hqfpTShLM0oylubedkKGKn
UvZ5Zv/CACI2epLxDlgZXZcySp+bJradxVdUZPPW/Tmnc2NIZD/gCXLH7YNEDUyv
ZnOh50N7xUg7qrhnr+IloXog+Y5wRQkj76ejuMlPPEOMz2xlnzMIpLEl6b+HkFwT
BWeWlfyzpTWteKMlq/Rw3ghQ2kFhayrckqnaWKNmErK55vZJok4UP+U/ilC4L/ZM
XLZgb39Awni8L9p59ZrK3mn1VbD/l6axff3fj2Db7lb7pcT1ssT2gazgQvPxHEYt
U2fKTgUyO2tWNHed2PCKSJ6F6rpG4RRcN53BTnOo27b38NrZnx06bh9OUW3Ws5Qf
43YN/h7UXI5gAnnHR4fgkR0H8prK
-----END CERTIFICATE-----
""")
impostorKey = load_privatekey(FILETYPE_PEM, """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
""")
impostorCert = load_certificate(FILETYPE_PEM, """
-----BEGIN CERTIFICATE-----
MIIE8TCCAtkCADANBgkqhkiG9w0BAQ0FADA9MRowGAYDVQQDExFDcnlwdG8gMTAx
IENsaWVudDEfMB0GCSqGSIb3DQEJARYQdXNlckBleGFtcGxlLmNvbTAiGA8yMDEz
MTIxODAwMDAwMFoYDzIwMTgxMjE4MDAwMDAwWjA9MRowGAYDVQQDExFDcnlwdG8g
MTAxIENsaWVudDEfMB0GCSqGSIb3DQEJARYQdXNlckBleGFtcGxlLmNvbTCCAiIw
DQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAL5nHJKxsgDBpQMKaerj0M9k8lDJ
WAYjWTck5XYlsN2gvNXOK2fl/iX7AKdSMG9qHZYsxFAakZzf8naqkyhXCZhdCQzL
TKF+evj80v8mMB7E1lMiGE8U4D6q/3GEkbSs1T/hIWzhcKnoOZ3HaZn4dfm4sWzW
dfcKyovOa9PpWhr1JoVZG3OOdzoMGLfyTnR/pX5AnpcmEKusW4/xzIYc8SsWT9wq
hQZywEt69llGVByv78b219hnZbwbpAZ4SAqfgZcyJAZTclpTuamiv0SCvPzbwnEF
JhCVFCZyXz6EfZNi7bo5DuPPGmS30Or4BF2/MD5wr+lMVDP1IsXnrmpCa5cWFRIU
PaJv05O+aIvuMsipfwd75iqmULltBzReFISV/OoXlt+kM1i7Li5oN4JC08SZpD1o
BjG0mWo9w1Rxe/C0KTA3oAGwq0/lAesqraHYZ9jT6ylE1PI/GBEnFu0RYjAzJ20H
COee4eRpSQvd/GLa6qY3K1XT6YYW9KwpnW953/W/FHyVbi0u3HNrbdzjrfCFONnG
yu6TwLe/rh0xtEXCa4zJEsLXkA9mvlTzlA2V6IGKKPqDYiWaVVKawW/+s8KkrQcT
gKqs/L0TqvUhXkp0mSU0GO1+gaoHhs09uyLNVOFDhU6VKd9B4ifSl1V+n6fEjY/N
qgS7fKm7bBFFFUSxAgMBAAEwDQYJKoZIhvcNAQENBQADggIBALU0ItdvHxNBJ/0f
dFVcrBxPzXrZMmXzLf8KqLVn46iDefb+NzW1yZd2ZaaPuLOSySXLXdokY0cmeUYv
04Ainl0EG4EVfV930vcg2Q0He1EJyiDTqEEozdP9e+vkjuLbrnrjCMn69FVmELhu
W1jQRaR5amcpOWXs4qhehthZWkDEBUIs5cwDNZXRFWzJq2IsT5bjy/XJYa4wiXD1
z/BWzRovOsdhZgX+YY3AhNGzyXxoKWjYh8+38Rt9bQJ9SH1ypbzx2BgYTT9hd0e1
uTi3Ss6ewQCuZqkoxcrkV0478Dxj7zUphHUl7AcbFz6vj2n1s9G0HjQDHRzYDMCj
KZ/SAbvT4G4S3pu9LPOtzmMFsTcPcZ8+njD0PrwvEXduMMSeOxpmO2a+/ARhqld1
6dS+R9YMtAvj3nInShEf8LtWTNMdzzQZrr4VVqtid2zxUeiY83L/xJCtXvbaxz5u
RpJXTDYxDZWSXNdppOydRonIAPqDOCMBrVUPPU3jNs0HtPROej1Xjh5EPI5affSc
pOUOQ1i/Og7gQtcyNtvwmgBn8yhTVZnwgS0GGTITIjJYMCnco8GgXGjhnBNp0zWv
y+UVyEjsKa5MbEyDxvIN36xACb3qG6za2S87L8DE0fwGvExD9FM7P6l5ZBAV+xd9
UvElfcF0Vk5PLLFNUTBMpoDv5GSZ
-----END CERTIFICATE-----
""")
bogusCert = load_certificate(FILETYPE_PEM, """
-----BEGIN CERTIFICATE-----
MIIE8zCCAtsCADANBgkqhkiG9w0BAQ0FADA+MRowGAYDVQQDExFDcnlwdG8gMTAx
IENsaWVudDEgMB4GCSqGSIb3DQEJARYRQk9HVVNAZXhhbXBsZS5jb20wIhgPMjAx
MzEyMTgwMDAwMDBaGA8yMDE4MTIxODAwMDAwMFowPjEaMBgGA1UEAxMRQ3J5cHRv
IDEwMSBDbGllbnQxIDAeBgkqhkiG9w0BCQEWEUJPR1VTQGV4YW1wbGUuY29tMIIC
IjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAvmcckrGyAMGlAwpp6uPQz2Ty
UMlYBiNZNyTldiWw3aC81c4rZ+X+JfsAp1Iwb2odlizEUBqRnN/ydqqTKFcJmF0J
DMtMoX56+PzS/yYwHsTWUyIYTxTgPqr/cYSRtKzVP+EhbOFwqeg5ncdpmfh1+bix
bNZ19wrKi85r0+laGvUmhVkbc453OgwYt/JOdH+lfkCelyYQq6xbj/HMhhzxKxZP
3CqFBnLAS3r2WUZUHK/vxvbX2GdlvBukBnhICp+BlzIkBlNyWlO5qaK/RIK8/NvC
cQUmEJUUJnJfPoR9k2LtujkO488aZLfQ6vgEXb8wPnCv6UxUM/UixeeuakJrlxYV
EhQ9om/Tk75oi+4yyKl/B3vmKqZQuW0HNF4UhJX86heW36QzWLsuLmg3gkLTxJmk
PWgGMbSZaj3DVHF78LQpMDegAbCrT+UB6yqtodhn2NPrKUTU8j8YEScW7RFiMDMn
bQcI557h5GlJC938YtrqpjcrVdPphhb0rCmdb3nf9b8UfJVuLS7cc2tt3OOt8IU4
2cbK7pPAt7+uHTG0RcJrjMkSwteQD2a+VPOUDZXogYoo+oNiJZpVUprBb/6zwqSt
BxOAqqz8vROq9SFeSnSZJTQY7X6BqgeGzT27Is1U4UOFTpUp30HiJ9KXVX6fp8SN
j82qBLt8qbtsEUUVRLECAwEAATANBgkqhkiG9w0BAQ0FAAOCAgEAm/qYWE6sc5Ms
ZfZVXLAO/y5n7M5Fn30krZ6QEPZGrTjmPTgokyPvl+w1syQKjlSl/4ezfO8nocZK
RmgTIXv740FxtzCuXNjYvdREUH9Sf3UiDjazRoeXdUAacaKGxglfnlw2F4XlVq3G
JCUpLafPrJJWBAt47RvaK2sT0VmsgrKWCnTrAvkx9lD3sr7lazo1y6VCoYu7JQUI
g5sO+db0B7CkG4+uRgEmRSsSX9VQhRSQgXY6gE+ac1mKtjIaygyM4ndEAVoaHtI0
3+ANFh7atilQNAuJvkQS1ZypgY6SQ2Ap10zZFO4M5EUq3iSpX/8IT1D7HsbLskm1
XySFXlQ3EUiVRbgZ6Q07FUNI0+BRrk6lH3r771Xwb1dqW0k1VyI2KM95Hd7Z38Bz
v8S8XtBKMzvTNqAP6qFpUXuxjIVUPu3AxEChnOtpJ1ney7QJCpyWzuQMvgC3/Hvw
W3x1/bG+IJRg7tlBBsTYG8fefENzBpJVslTgLVHaHgnO3XrGI0EJR3B4hZ5HDzyH
XG82KXZ7uSM3RKDKsKN+UQdtUhBVrKskA3M/25ZIN8Ah+A5BO7jdh3hIA8fMPBaX
xMSAjNLyo3RjjpJMgeEs2+zqBqW4NKRB2ojeWZUA0dXgCO1nFlorAVSXNAHICKrk
zSrTx+wpRsqC46MW1cq5bvEJ7yqas/Q=
-----END CERTIFICATE-----
""")
