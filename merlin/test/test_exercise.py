from merlin import exercise
from twisted.python import reflect
from twisted.trial.unittest import SynchronousTestCase
from txampext.commandtests import CommandTestMixin


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



USER_STORE = object()



def fakeValidator(userStore, submission):
    assert userStore is USER_STORE
    return "valid" in submission



fakeValidator.name = reflect.fullyQualifiedName(fakeValidator)



class FakeValidatorTests(SynchronousTestCase):
    """
    Test cases for the fake validator.
    """
    def test_validSubmission(self):
        """
        The fake validator validates submissions with ``"valid"`` in them.
        """
        self.assertTrue(fakeValidator(USER_STORE, u"valid"))


    def test_invalidSubmission(self):
        """
        The fake validator does not validate submissions that do not have
        ``"valid"`` in them.
        """
        self.assertTrue(fakeValidator(USER_STORE, u"valid"))


    def test_fakeValidatorChecksUserStore(self):
        """
        The fake validator checks that the user store sentinel is passed.
        """
        self.assertRaises(AssertionError, fakeValidator, object(), u"")



class StepValidatorTests(SynchronousTestCase):
    def test_validator(self):
        """
        The `validator` attribute gets the validator for this step. It
        also caches the validator.
        """
        step = exercise.Step(text=u"", validatorName=fakeValidator.name)
        self.assertRaises(AttributeError, lambda: step._validator)

        self.assertIdentical(step.validator, fakeValidator)
        self.assertIdentical(step._validator, fakeValidator)


    def test_createWithValidator(self):
        """
        When creating a step with a validator, the step stores the fully
        qualified name of the validator. The step's validator cache is
        primed.
        """
        step = exercise.Step.createWithValidator(u"", fakeValidator)

        self.assertEqual(step.validatorName, fakeValidator.name)
        self.assertEqual(step._validator, fakeValidator)



class StepValidationTests(SynchronousTestCase):
    """
    Steps can validate submissions.
    """
    def setUp(self):
        self.step = exercise.Step.createWithValidator(u"", fakeValidator)


    def test_validate(self):
        """
        A step validates submissions using its validator.
        """
        self.assertTrue(self.step.validate(USER_STORE, "valid"))
