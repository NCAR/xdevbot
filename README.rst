|CircleCI| |Linting| |Coverage| |Docs| |License| |PyPI| |Heroku|

AIOHTTP Application Template
============================

This template repository is meant to serve as a starting point for anyone wanting to build an ``aiohttp``-based
web application and run that web application on Heroku (or a similar service).  It provides basic structure and
setup for a web application using a MongoDB database with Python ``motor``, and the base code is set up with
``pytest`` unit testing and continuous integration with CircleCI (and GitHub Actions).

How to use this template
------------------------

You should just be able to create your own repository based on this template by just choosing this template
during the new repository creation form on GitHub.  You will probably want to change the name of this application
to something more suited to your needs.  By default, the name of the web application (and the PyPI package, and
the name of the Python package you might import) is determined *solely* from the name of the main package
directory.  Currently, it is ``myapp``, so all you would need to do is change the name of this directory.

When creating a new repository from this template, I highly recommend that you select the *"Include all branches"*
radio button.  If you do this, you will automatically get a working Sphinx deployment of the application
documentation on GitHub Pages.  If you do not do this, you may have to manually fix some settings for your
GitHub Pages site to work properly (e.g., manually adding a ``.nojekyll`` file to the ``gh-pages`` branch).

Some notes on the design
------------------------

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

   $ python -m myapp

However, this application uses ``click`` for its CLI, which means you can get the
full help description with:

.. code-block:: bash

   $ python -m myapp --help
   Usage: myapp [OPTIONS]

   Options:
     --version          Show the version and exit.
     --host TEXT        Server IP address
     --port INTEGER     Server port number
     --logging INTEGER  Logging output level
     --mongouri TEXT    MongoDB URI
     --mongodb TEXT     MongoDB Database Name
     --config PATH      User-defined configuration file location
     --help             Show this message and exit.



.. |CircleCI| image:: https://img.shields.io/circleci/build/github/ncar-xdev/aiohttp_app_template?label=tests
    :target: https://circleci.com/gh/ncar-xdev/aiohttp_app_template
    :alt: Tests

.. |Linting| image:: https://img.shields.io/github/workflow/status/ncar-xdev/aiohttp_app_template/code-style?label=linting
    :target: https://github.com/ncar-xdev/aiohttp_app_template/actions?query=workflow%3Acode-style
    :alt: Linting

.. |Coverage| image:: https://img.shields.io/codecov/c/gh/ncar-xdev/aiohttp_app_template
    :target: https://codecov.io/gh/ncar-xdev/aiohttp_app_template
    :alt: Coverage

.. |Docs| image:: https://img.shields.io/website?down_color=red&down_message=offline&label=docs&up_color=green&up_message=online&url=https%3A%2F%2Fncar-xdev.github.io%2Faiohttp_app_template
    :target: https://ncar-xdev.github.io/aiohttp_app_template
    :alt:

.. |License| image:: https://img.shields.io/github/license/ncar-xdev/aiohttp_app_template
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: License

.. |PyPI| image:: https://img.shields.io/pypi/v/abcdefghijklmnop?label=pypi
    :target: https://pypi.org/project/abcdefghijklmnop
    :alt: PyPI

.. |Heroku| image:: https://img.shields.io/website?down_color=red&down_message=offline&label=heroku&up_color=green&up_message=online&url=https%3A%2F%2Fmyapp.herokuapp.com%2F
    :target: https://myapp.herokuapp.com
    :alt: Heroku
