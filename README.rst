|CircleCI| |GitHub| |Coverage| |License| |PyPI|

The NCAR Xdev Bot
=================

This Bot is based on the ``ncar-xdev/aiohttp_app_template`` template for a simple
web application based on ``aiohttp`` and ``motor``, using a MongoDB database.

aiohttp
~~~~~~~

This application is build using ``aiohttp``, an asynchronous web server/client
framework for Python 3.5+.  If you are unfamiliar with asynchronous programming in
Python (namely, Python 3.5+'s ``asyncio``), then you should read up on it here:

- https://docs.python.org/3/library/asyncio.html
- https://realpython.com/async-io-python/

The ``aiohttp`` package provides a web server and client that uses this fundamental
``asyncio`` functionality.  To learn more about ``aiohttp``, you can read up on it here:

- https://docs.aiohttp.org/en/v3.0.1/tutorial.html#aiohttp-tutorial


motor
~~~~~

This app is designed to work with MongoDB for persistent data storage.  MongoDB
provides a cloud-based DBaaS which has a free "sandbox" level (512 MB).
The app does not need much storage, so we use this service for free, but we may
need to upgrade to a paid service in the future, or switch to a different DB
solution.

The recommended ``asyncio``-compatible driver for MongoDB is ``motor``.  The tutorial
for ``motor`` with ``asyncio`` can be found here:

- https://motor.readthedocs.io/en/stable/tutorial-asyncio.html


Heroku
~~~~~~

This app is also designed to run on Heroku.  It is not large or demanding, so we
do not need to pay for anything, yet.  The launch command that is needed for the
app to run on Heroku is stored in the ``Procfile`` file, and the version of Python
needed to run is specified in the ``runtime.txt`` file.


CircleCI
~~~~~~~~

This app also has continuous integration enabled with CircleCI.  This means that
Heroku can be used to autodeploy when CI tests pass.


Installation
------------

This application can be installed with ``pip`` or directly with ``setup.py``:

.. code-block:: bash

   $ python setup.py install

or

.. code-block:: bash

   $ pip install .


Running Locally
---------------

To run this application locally, you need simply run:

.. code-block:: bash

   $ python -m xdevbot

However, this application uses ``click`` for its CLI, which means you can get the
full help description with:

.. code-block:: bash

   $ python -m xdevbot --help
   Usage: xdevbot [OPTIONS]

   Options:
     --version          Show the version and exit.
     --host TEXT        Server IP address
     --port INTEGER     Server port number
     --logging INTEGER  Logging output level
     --mongouri TEXT    MongoDB URI
     --mongodb TEXT     MongoDB Database Name
     --config PATH      User-defined configuration file location
     --help             Show this message and exit.



.. |CircleCI| image:: https://badgen.net/circleci/github/ncar-xdev/xdevbot/master
    :target: https://circleci.com/gh/ncar-xdev/xdevbot
    :alt: Tests

.. |GitHub| image:: https://badgen.net/github/checks/ncar-xdev/xdevbot/master
    :target: https://github.com/ncar-xdev/xdevbot/actions?query=workflow%3Acode-style
    :alt: GitHub

.. |Coverage| image:: https://badgen.net/codecov/c/github/ncar-xdev/xdevbot
    :target: https://codecov.io/gh/ncar-xdev/xdevbot
    :alt: Coverage

.. |License| image:: https://badgen.net/github/license/ncar-xdev/xdevbot
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: License

.. |PyPI| image:: https://badgen.net/pypi/v/xdevbot?label=pypi
    :target: https://pypi.org/project/xdevbot
    :alt: PyPI
