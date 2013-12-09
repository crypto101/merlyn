from axiom.store import Store
from clarent.exercise import GetExercises, GetExerciseDetails
from clarent.exercise import UnknownExercise, NotifySolved
from merlyn.exercise import Exercise, Locator, solveAndNotify
from merlyn.auth import User, NotLoggedIn
from twisted.trial.unittest import SynchronousTestCase
from txampext.respondertests import ResponderTests



class ExerciseTests(SynchronousTestCase):
    def test_wasSolvedBy(self):
        """The exercise knows when it was solved by a particular user.

        """
        store = Store()

        exercise = Exercise(
            store=store,
            identifier=b"identifier",
            title=u"\N{SNOWMAN}",
            description=u"\N{CLOUD}")

        someUser = User(store=store, email=u"foo@example.com")
        self.assertFalse(exercise.wasSolvedBy(someUser))

        exercise.solvedBy(someUser)
        self.assertTrue(exercise.wasSolvedBy(someUser))

        someOtherUser = User(store=store, email=u"bar@example.com")
        self.assertFalse(exercise.wasSolvedBy(someOtherUser))



class SolveAndNotifyTests(SynchronousTestCase):
    def test_solveAndNotify(self):
        store = Store()
        user = User(store=store, email=u"test@example.com")
        proto = FakeProto(store, user)
        exercise = Exercise(
            store=store,
            identifier=b"identifier",
            title=u"\N{SNOWMAN}",
            description=u"\N{CLOUD}")

        self.assertFalse(exercise.wasSolvedBy(user))
        solveAndNotify(proto, exercise)
        self.assertTrue(exercise.wasSolvedBy(user))

        self.assertIdentical(proto.command, NotifySolved)
        self.assertEqual(proto.kwargs, {
            b"identifier": b"identifier",
            b"title": u"\N{SNOWMAN}"
        })


class FakeProto(object):
    def __init__(self, store, user):
        self.store = store
        self.user = user

        self.command = self.kwargs = None


    def callRemote(self, command, **kwargs):
        self.command = command
        self.kwargs = kwargs



class _LocatorTests(object):
    def setUp(self):
        self.locator = Locator()
        self.locator.store = store = Store()
        self.locator.user = user = User(store=store)

        one = Exercise(store=store, title=u"Exercise 1", identifier=b"1")
        one.solvedBy(user)

        Exercise(store=store, title=u"Exercise 2", identifier=b"2")
        Exercise(store=store, title=u"Exercise 3", identifier=b"3")



class GetExercisesTests(_LocatorTests, SynchronousTestCase):
    def test_loginRequired(self):
        """A user must be logged in to call this method.

        """
        self.locator.user = None
        self.assertRaises(NotLoggedIn, self.locator.getExercises)


    def test_getExercises(self):
        """A user can get some new exercises.

        """
        exercises = self.locator.getExercises(solved=False)
        exercises.sort(key=lambda d: d[b"identifier"])
        self.assertEqual(exercises, [
            {b"title": u"Exercise 2", b"identifier": b"2"},
            {b"title": u"Exercise 3", b"identifier": b"3"}
        ])


    def test_getSolvedExercises(self):
        """A user can get previously solved exercises.

        """
        exercises = self.locator.getExercises(solved=True)
        exercises.sort(key=lambda d: d["identifier"])
        self.assertEqual(exercises, [
            {b"title": u"Exercise 1", b"identifier": b"1"},
        ])



class GetExerciseDetailsTests(SynchronousTestCase):
    def test_loginRequired(self):
        """A user must be logged in to call this method.

        """
        self.locator.user = None
        self.assertRaises(NotLoggedIn, self.locator.getExerciseDetails)


    def test_getSolvedExerciseDetails(self):
        """A user can get details about a solved exercise.

        """
        details = self.locator.getExerciseDetails(identifier=b"1")
        self.assertEqual(details, {
            b"identifier": b"1",
            b"title": u"Exercise 1",
            b"solved": True
        })


    def test_getUnsolvedExerciseDetails(self):
        """A user can get details about an unsolved exercise.

        """
        details = self.locator.getExerciseDetails(identifier=b"2")
        self.assertEqual(details, {
            b"identifier": "2",
            b"title": u"Exercise 2",
            b"solved": False
        })


    def test_missingExercise(self):
        """When attempting to get details for an exercise that doesn't exist,
        an error is raised.

        """
        self.assertRaises(UnknownExercise,
                          self.locator.getExerciseDetails, identifier="BOGUS")



locator = Locator()



class GetExercisesResponderTests(ResponderTests):
    command =  GetExercises
    locator = locator



class GetExerciseDetailsResponderTests(ResponderTests):
    command =  GetExerciseDetails
    locator = locator
