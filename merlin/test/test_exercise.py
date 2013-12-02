from merlyn import exercise, interfaces as imerlyn
from twisted.trial.unittest import SynchronousTestCase
from zope.interface.verify import verifyObject


class StepTests(SynchronousTestCase):
    def test_implements(self):
        """
        The Step item class implements the IStep interface.
        """
        lastStep = exercise.Step()
        firstStep = exercise.Step(nextStep=lastStep)
        verifyObject(imerlyn.IStep, firstStep)
        verifyObject(imerlyn.IStep, lastStep)
