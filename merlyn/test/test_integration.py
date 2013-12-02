from axiom import attributes, item, store
from merlyn.exercise import Exercise, Step
from merlyn.interfaces import IRenderer, IValidator
from merlyn.renderers import StringTemplateRenderer
from twisted.trial.unittest import SynchronousTestCase
from zope.interface import implementer, verify


class ExerciseTest(SynchronousTestCase):
    def test_twoStepExercise(self):
        """Create an exercise consisting of two steps, then solve it.

        """
        rootStore = store.Store()

        firstStep = Step(store=rootStore)
        firstStep.inMemoryPowerUp(FirstValidator(), IValidator)
        renderer = StringTemplateRenderer(template=u"Hello!")
        firstStep.inMemoryPowerUp(renderer, IRenderer)

        secondStep = Step(store=rootStore)
        secondStep.inMemoryPowerUp(SecondValidator(), IValidator)
        secondStep.inMemoryPowerUp(SecondRenderer(), IRenderer)
        firstStep.nextStep = secondStep

        exercise = Exercise(store=rootStore, title=u"X", firstStep=firstStep)

        userStore = store.Store()
        StoredValue(store=userStore, value=42)

        currentStep = exercise.firstStep
        rendered = IRenderer(currentStep).render(userStore)
        self.assertEqual(rendered, u"Hello!")
        currentValidator = IValidator(currentStep)
        result = currentValidator.validate(b"Will $50 fix it?", userStore)
        self.assertFalse(result)
        result = currentValidator.validate(b"OK, here's $100!", userStore)
        self.assertTrue(result)

        currentStep = currentStep.nextStep
        rendered = IRenderer(currentStep).render(userStore)
        self.assertEqual(rendered, u"The answer is 42.")
        currentValidator = IValidator(currentStep)
        self.assertFalse(currentValidator.validate(b"123", userStore))
        self.assertTrue(currentValidator.validate(b"42", userStore))



@implementer(IValidator)
class FirstValidator(object):
    """The validator for the first step.

    """
    def validate(self, submission, _userStore):
        return b"$100" in submission



class StoredValue(item.Item):
    """A stored integer value.

    """
    value = attributes.integer()



@implementer(IRenderer)
class SecondRenderer(object):
    """The renderer for the second step.

    """
    def render(self, userStore):
        value = userStore.findUnique(StoredValue).value
        return u"The answer is {0}.".format(value)



@implementer(IValidator)
class SecondValidator(object):
    """
    The validator for the second step.
    """
    def validate(self, submission, userStore):
        value = userStore.findUnique(StoredValue).value
        return int(submission) == value



class TestObjectsTests(SynchronousTestCase):
    """Tests for the test objects.

    """
    def test_firstValidator(self):
        """The first validator implements the IValidator interface.

        """
        verify.verifyObject(IValidator, FirstValidator())


    def test_secondValidator(self):
        """The second validator implements the IValidator interface.

        """
        verify.verifyObject(IValidator, SecondValidator())


    def test_secondRenderer(self):
        """The second step renderer implements the IRenderer interface.

        """
        verify.verifyObject(IRenderer, SecondRenderer())
