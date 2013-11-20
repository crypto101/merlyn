"""
Interfaces.
"""
from zope.interface import Attribute, Interface


class IStep(Interface):
    """
    A step in an excerise.
    """
    nextStep = Attribute(
        """
        The step following this one, or None if this is the last step.
        """)



class IRenderer(Interface):
    """
    Renders a step in an exercise.
    """
    def render(userStore):
        """
        Renders a step, using the context of a user store.
        """



class IValidator(Interface):
    """
    A validator for a step in an exercise.
    """
    def validate(submission, userStore):
        """
        Validates a submission using the context of a user store.
        """
