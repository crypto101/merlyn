"""
Basic exercise and step implementations.
"""
from axiom import attributes, item
from merlin import interfaces as imerlin
from zope.interface import implementer



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
