"""
Basic exercise and step implementations.
"""
from axiom import attributes, item
from merlin import interfaces as imerlin
from twisted.protocols import amp
from txampext.errors import Error
from zope.interface import implementer


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



@implementer(imerlin.IStep)
class Step(item.Item):
    """
    A single step in an exercise.
    """
    nextStep = attributes.reference()
