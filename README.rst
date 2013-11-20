========
 merlin
========

A server backend for interactive online exercises.

Testing and building the documentation
======================================

Testing is done using tox_. Install it, and run it from the command
line in the repository root. This will create a virtualenv_ for each
supported environment, install the necessary things in it, run the
tests, and build the documentation.

Speeding up builds
------------------

For a faster experience, it is recommended that you configure pip_ to
use wheel_ by default, by placing the following in your
``~/.pip/pip.conf`` or equivalent::

  [install]
  wheel-dir = /tmp/wheelhouse
  use-wheel = True

  [wheel]
  wheel-dir = /tmp/wheelhouse
  use-wheel = True

After that, run ``pip wheel -r requirements*`` once. It will create
wheels, which are faster to install than regular packages.

.. _tox: https://testrun.org/tox/
.. _virtualenv: https://pypi.python.org/pypi/virtualenv/
.. _pip: http://www.pip-installer.org/en/latest/
.. _wheel: http://wheel.readthedocs.org/en/latest/

Release notes
=============

0.0.2
-----

Features:

- Exercise and Step classes
- Step validation draft
- Step solution submission interface

0.0.1
-----

Initial public release. Nothing much to see here.
