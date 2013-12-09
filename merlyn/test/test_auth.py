from merlyn.auth import loginRequired, NotRegistered
from twisted.trial.unittest import SynchronousTestCase

class LoginRequiredTests(SynchronousTestCase):
    def setUp(self):
        self.calls = 0


    def aMethod(self):
        """
        Increments the call count.
        """
        self.calls += 1


    decoratedMethod = loginRequired(aMethod)


    def test_wraps(self):
        """The decorated method has the docstring and name of the wrapped
        method.

        """
        self.assertEqual(self.decoratedMethod.__name__, "aMethod")
        self.assertEqual(self.decoratedMethod.__doc__, self.aMethod.__doc__)


    def test_notLoggedIn(self):
        """When there is no user, the decorated method raises NotRegistered.
        The wrapped method is not called.

        """
        self.assertEqual(self.calls, 0)
        self.user = None
        self.assertRaises(NotRegistered, self.decoratedMethod)
        self.assertEqual(self.calls, 0)


    def test_loggedIn(self):
        """When there is a user, the wrapped method is called.

        """
        self.assertEqual(self.calls, 0)
        self.user = object()
        self.decoratedMethod()
        self.assertEqual(self.calls, 1)
