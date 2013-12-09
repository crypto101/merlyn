"""
Basic exercise and step implementations.
"""
from axiom import attributes, item, queryutil as q
from axiom.errors import ItemNotFound
from clarent import exercise as ce
from twisted.protocols import amp


class Exercise(item.Item):
    """
    An exercise.
    """
    identifier = attributes.string(allowNone=False)
    title = attributes.text(allowNone=False)
    description = attributes.text(allowNone=False)

    def solvedBy(self, user):
        """Notes that this user has just solved this exercise.

        You probably want to notify the user when this happens. For
        that, see ``solveAndNotify``.

        """
        _Solution(store=self.store, who=user, what=self)


    def wasSolvedBy(self, user):
        """
        Checks if this exercise has previously been solved by the user.
        """
        thisExercise = _Solution.what == self
        byThisUser = _Solution.who == user
        condition = q.AND(thisExercise, byThisUser)
        return self.store.query(_Solution, condition, limit=1).count() == 1



class _Solution(item.Item):
    """
    A log of an exercise being solved.
    """
    who = attributes.reference(allowNone=False)
    what = attributes.reference(allowNone=False)



def solveAndNotify(proto, exercise):
    """The user at the given AMP protocol has solved the given exercise.

    This will log the solution and notify the user.
    """
    exercise.solvedBy(proto.user)
    proto.callRemote(ce.NotifySolved, identifier=exercise.identifier)



class Locator(amp.CommandLocator):
    def getExercises(self, completed=False):
        pass


    def getExerciseDetails(self, identifier):
        exercise = self._getExercise(identifier)
        response = {
            b"title": exercise.title,
            b"description": exercise.description,
            b"solved": exercise.wasSolvedBy(self.user)
        }
        return response


    def _getExercise(self, identifier):
        try:
            return self.store.findUnique(Exercise, identifier=identifier)
        except ItemNotFound:
            raise ce.UnknownExercise()
