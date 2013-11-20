from axiom import attributes, item
from twisted.protocols import amp
from twisted.python import reflect
from txampext.errors import Error


class UnknownStep(Error):
    """
    The step for which a submission was made was not recognized.
    """



class WrongStep(Error):
    """
    The step for which a submission was made was recognized, but the
    user was not on that step of the exercise.

    This can occur when a user accidentally submits something for a
    step they had previously submitted something for.
    """



class IncorrectSubmission(Error):
    """
    The submission was understood, but incorrect.
    """



class Submit(amp.Command):
    arguments = [
        (b"step", amp.Integer()),
        (b"submission", amp.String())
    ]
    response = []
    errors = dict([
        IncorrectSubmission.asAMP(),
        UnknownStep.asAMP(),
        WrongStep.asAMP()
    ])



class Exercise(item.Item):
    """
    An exercise, consisting of one or more steps.
    """
    title = attributes.text(allowNone=False)
    firstStep = attributes.reference(allowNone=False)



class Step(item.Item):
    """
    A single step in an exercise.
    """
    text = attributes.text(allowNone=False)
    nextStep = attributes.reference()

    validatorName = attributes.bytes(allowNone=False)
    _validator = attributes.inmemory()

    @classmethod
    def createWithValidator(cls, text, validator):
        """
        Creates a new step with the given text and validator callable. The
        step will not yet be stored.
        """
        name = reflect.fullyQualifiedName(validator)
        return cls(text=text, _validator=validator, validatorName=name)


    @property
    def validator(self):
        """
        Gets the validator for this step.
        """
        validator = self._validator = reflect.namedAny(self.validatorName)
        return validator


    def validate(self, userStore, submission):
        """
        Attempts to validate.
        """
        return self.validator(userStore, submission)
