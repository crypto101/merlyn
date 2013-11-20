from merlin import exercise, interfaces as imerlin
from twisted.trial.unittest import SynchronousTestCase
from txampext.commandtests import CommandTestMixin
from zope.interface.verify import verifyObject


class SubmissionTests(SynchronousTestCase, CommandTestMixin):
    command = exercise.Submit

    argumentObjects = {
        b"step": 1,
        b"submission": b"xyzzy"
    }
    argumentStrings = {
        b"step": "1",
        b"submission": b"xyzzy"
    }

    responseObjects = {}
    responseStrings = {}

    errors = dict([
        exercise.UnknownStep.asAMP(),
        exercise.WrongStep.asAMP(),
        exercise.IncorrectSubmission.asAMP()
    ])
    fatalErrors = {}



class StepTests(SynchronousTestCase):
    def test_implements(self):
        """
        The Step item class implements the IStep interface.
        """
        step =  exercise.Step(text=u"", validatorName=b"")
        verifyObject(imerlin.IStep, step)



class IntegrationTest(SynchronousTestCase):
    def test_multipleSteppedExercise(self):
        """
        An exercise consisting of multiple steps.
        """
