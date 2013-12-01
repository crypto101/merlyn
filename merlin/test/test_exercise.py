from merlin import exercise, interfaces as imerlin
from twisted.trial.unittest import SynchronousTestCase
from zope.interface.verify import verifyObject


class StepTests(SynchronousTestCase):
    def test_implements(self):
        """
        The Step item class implements the IStep interface.
        """
        step = exercise.Step(text=u"", validatorName=b"")
        verifyObject(imerlin.IStep, step)
