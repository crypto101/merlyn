from merlin import exercise
from twisted.python import reflect
from twisted.trial import unittest


USER_STORE = object()



def fakeValidator(userStore, submission):
    assert userStore is USER_STORE
    return "valid" in submission



fakeValidator.name = reflect.fullyQualifiedName(fakeValidator)



class FakeValidatorTests(unittest.SynchronousTestCase):
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



class StepValidatorTests(unittest.SynchronousTestCase):
    def test_getValidator(self):
        """
        The ``_getValidator`` method reproduces the validator. It also
        caches the validator.
        """
        step = exercise.Step(text=u"", validatorName=fakeValidator.name)
        self.assertRaises(AttributeError, lambda: step._validator)

        self.assertIdentical(step._getValidator(), fakeValidator)
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



class StepValidationTests(unittest.SynchronousTestCase):
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
