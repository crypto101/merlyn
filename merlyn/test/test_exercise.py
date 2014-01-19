import os

from axiom.store import Store
from clarent.exercise import GetExercises, GetExerciseDetails
from clarent.exercise import UnknownExercise, NotifySolved
from merlyn.exercise import Exercise, Locator, solveAndNotify
from merlyn.exercise import SolvableResourceMixin, Secret
from merlyn.auth import User
from twisted.trial.unittest import SynchronousTestCase
from txampext.respondertests import ResponderTestMixin



defaultExerciseKwargs = {
    "identifier": b"identifier",
    "title": u"\N{SNOWMAN}",
    "description": u"\N{CLOUD}"
}


def makeExercise(**kwargs):
    kw = defaultExerciseKwargs.copy()
    kw.update(kwargs)
    return Exercise(**kw)



class ExerciseTests(SynchronousTestCase):
    def test_wasSolvedBy(self):
        """The exercise knows when it was solved by a particular user.

        """
        store = Store()
        exercise = makeExercise(store=store)

        someUser = User(store=store, email="foo@example.com")
        self.assertFalse(exercise.wasSolvedBy(someUser))

        exercise.solvedBy(someUser)
        self.assertTrue(exercise.wasSolvedBy(someUser))

        someOtherUser = User(store=store, email="bar@example.com")
        self.assertFalse(exercise.wasSolvedBy(someOtherUser))



class SolveAndNotifyTests(SynchronousTestCase):
    def setUp(self):
        self.store = store = Store()
        self.user = User(store=store, email="test@example.com")
        self.proto = FakeProto(store, self.user)
        self.exercise = makeExercise(store=store)


    def wasSolved(self):
        """The current exercise has been marked as sovled by the current user.

        """
        return self.exercise.wasSolvedBy(self.user)


    def wasNotified(self):
        if self.proto.command is not NotifySolved:
            return False

        expectedKwargs = {
            b"identifier": b"identifier",
            b"title": u"\N{SNOWMAN}"
        }

        return self.proto.kwargs == expectedKwargs


    def test_solveAndNotify(self):
        self.assertFalse(self.wasSolved())
        self.assertFalse(self.wasNotified())

        solveAndNotify(self.proto, self.exercise)

        self.assertTrue(self.wasSolved())
        self.assertTrue(self.wasNotified())


    def test_resourceMixin(self):
        resource = SolvableResource(self.store)
        request = FakeRequest()
        request.transport = FakeTransport()
        request.transport.remote = self.proto

        self.assertFalse(self.wasSolved())
        self.assertFalse(self.wasNotified())

        resource.solveAndNotify(request)

        self.assertTrue(self.wasSolved())
        self.assertTrue(self.wasNotified())



class FakeProto(object):
    def __init__(self, store, user):
        self.store = store
        self.user = user

        self.command = self.kwargs = None


    def callRemote(self, command, **kwargs):
        self.command = command
        self.kwargs = kwargs



class FakeRequest(object):
    pass



class FakeTransport(object):
    pass



class SolvableResource(SolvableResourceMixin):
    exerciseIdentifier = b"identifier"



class _LocatorTests(object):
    def setUp(self):
        self.locator = Locator()
        self.locator.store = store = Store()
        self.locator.user = user = User(store=store, email=b"x@y.z")

        one = makeExercise(store=store, title=u"Exercise 1", identifier=b"1")
        one.solvedBy(user)

        makeExercise(store=store, title=u"Exercise 2", identifier=b"2")
        makeExercise(store=store, title=u"Exercise 3", identifier=b"3")



class GetExercisesTests(_LocatorTests, SynchronousTestCase):
    def test_getExercises(self):
        """A user can get some new exercises.

        """
        response = self.locator.getExercises(solved=False)
        exercises = list(response["exercises"])
        exercises.sort(key=lambda d: d[b"identifier"])
        self.assertEqual(exercises, [
            {b"title": u"Exercise 2", b"identifier": b"2"},
            {b"title": u"Exercise 3", b"identifier": b"3"}
        ])


    def test_getSolvedExercises(self):
        """A user can get previously solved exercises.

        """
        response = self.locator.getExercises(solved=True)
        exercises = list(response["exercises"])
        exercises.sort(key=lambda d: d["identifier"])
        self.assertEqual(exercises, [
            {b"title": u"Exercise 1", b"identifier": b"1"},
        ])



class GetExerciseDetailsTests(_LocatorTests, SynchronousTestCase):
    def test_getSolvedExerciseDetails(self):
        """A user can get details about a solved exercise.

        """
        details = self.locator.getExerciseDetails(identifier=b"1")
        self.assertEqual(details, {
            b"identifier": b"1",
            b"title": u"Exercise 1",
            b"description": u"\N{CLOUD}",
            b"solved": True
        })


    def test_getUnsolvedExerciseDetails(self):
        """A user can get details about an unsolved exercise.

        """
        details = self.locator.getExerciseDetails(identifier=b"2")
        self.assertEqual(details, {
            b"identifier": "2",
            b"title": u"Exercise 2",
            b"description": u"\N{CLOUD}",
            b"solved": False
        })


    def test_missingExercise(self):
        """When attempting to get details for an exercise that doesn't exist,
        an error is raised.

        """
        self.assertRaises(UnknownExercise,
                          self.locator.getExerciseDetails, identifier="BOGUS")



locator = Locator()



class GetExercisesResponderTests(ResponderTestMixin, SynchronousTestCase):
    command =  GetExercises
    locator = locator



class GetExerciseDetailsResponderTests(ResponderTestMixin, SynchronousTestCase):
    command =  GetExerciseDetails
    locator = locator



class SecretTests(SynchronousTestCase):
    def setUp(self):
        self.store = Store()
        self.user = User(store=self.store, email="test@example.com")


    def test_new(self):
        """When the user has no secret yet, gets a new secret.

        Asserts that the secret requests a sufficient number of bytes
        from urandom.

        """
        self.patch(os, "urandom", self._urandom)
        self.assertEqual(self.store.query(Secret).count(), 0)

        secret = Secret.forUser(self.user)
        self.assertEqual(secret.entropy, "sikrit")
        self.assertEqual(secret.user, self.user)


    def _urandom(self, nBytes):
        """
        Asserts that 256 bits worth of entropy is being requested.
        """
        self.assertEqual(nBytes, 256 // 8)
        return "sikrit"


    def test_same(self):
        """When the user already has a secret, gets that secret.

        """
        secret = Secret(store=self.store, entropy="xyzzy", user=self.user)
        self.assertIdentical(Secret.forUser(self.user), secret)


    def test_indexed(self):
        """The user attribute of secrets is indexed.

        """
        self.assertTrue(Secret.user.indexed)
