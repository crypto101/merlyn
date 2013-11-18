from axiom import attributes, item
from twisted.python import reflect


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


    def _getValidator(self):
        """
        Gets the validator for this step.
        """
        validator = self._validator = reflect.namedAny(self.validatorName)
        return validator


    def validate(self, userStore, submission):
        """
        Attempts to validate.
        """
        validator = self._getValidator()
        return validator(userStore, submission)
