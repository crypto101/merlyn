===========
 Exercises
===========

Exercises are modeled as sequences of requests and responses.
Therefore, exercises consist of multiple steps. This allows
interactive exercises, customized by the user's previous submissions.

Steps
=====

Steps are objects that optionally refer to a following step (unless
they are the last step in an exercise). They also must be adaptable
to the following interfaces:

- :py:class:`IRenderer<merlin.interfaces.IRenderer>`, for rendering a
  step to a user.
- :py:class:`IValidator<merlin.interfaces.IValidator>`, for validating
  a submission by the user.

Usually, this is accomplished using Axiom powerups. While there's
nothing stopping you from writing implementations that simply
implement all of these interfaces, this design is intended to nudge
you in the direction of extensive composition.

Step interfaces
---------------

.. autointerface:: merlin.interfaces.IStep
                   :members:

.. autointerface:: merlin.interfaces.IRenderer
                   :members:

.. autointerface:: merlin.interfaces.IValidator
                   :members:
