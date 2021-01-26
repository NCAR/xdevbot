|CircleCI| |GitHub| |Coverage| |License|

The NCAR Xdevbot
================

The Xdevbot is designed to help monitor activity (Issues
and Pull Requests) on GitHub repositories that might be scattered
across many different organizations.  The Xdevbot assumes a
single *Board Repository* where multiple GitHub Project Boards
will be hosted.

Each Project Board on the *Board Repository* is used to *watch*
all of the Issues/PRs in a *Watchlist* of GitHub Repositories.
This allows you to organize your watched repositories categorically
or topically.  Users may add single Issues/PRs to any Project Board
manually.

The Xdevbot provides simple automation for all Issues/PRs on the
Boards, such that all newly created Issues are added to the *New*
column, newly created PRs and reopened Issues are added/moved to the
*In Progress* column, and any closed/merged Issue/PR is moved to the
*Done* column.

A *Main* Board can be used to aggregate *all* Issues/PRs across
all of the Boards into a single, comprehensive Project Board.

This is an aiohttp_ app designed to run on Heroku_ with Gunicorn_.


Running Locally
---------------

To run this application locally, you need simply run:

.. code-block:: bash

   $ gunicorn xdevbot:init_app --worker-class aiohttp.GunicornWebWorker

.. _aiohttp: https://docs.aiohttp.org/en/stable/

.. _Heroku: https://www.heroku.com/

.. _Gunicorn: https://gunicorn.org/

.. |CircleCI| image:: https://badgen.net/circleci/github/NCAR/xdevbot/main
    :target: https://circleci.com/gh/NCAR/xdevbot
    :alt: Tests

.. |GitHub| image:: https://badgen.net/github/checks/NCAR/xdevbot/main
    :target: https://github.com/NCAR/xdevbot/actions?query=workflow%3Acode-style
    :alt: GitHub

.. |Coverage| image:: https://badgen.net/codecov/c/github/NCAR/xdevbot
    :target: https://codecov.io/gh/NCAR/xdevbot
    :alt: Coverage

.. |License| image:: https://badgen.net/github/license/NCAR/xdevbot?012345
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: License
