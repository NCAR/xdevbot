|CircleCI| |GitHub| |Coverage| |License| |PyPI|

The NCAR Xdevbot
================

This Bot is based on the ``kmpaul/aiohttp_app_template`` template for a simple
web application based on ``aiohttp`` and ``motor``, using a MongoDB database.


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



.. |CircleCI| image:: https://badgen.net/circleci/github/NCAR/xdevbot/master?012345
    :target: https://circleci.com/gh/NCAR/xdevbot
    :alt: Tests

.. |GitHub| image:: https://badgen.net/github/checks/NCAR/xdevbot/master
    :target: https://github.com/NCAR/xdevbot/actions?query=workflow%3Acode-style
    :alt: GitHub

.. |Coverage| image:: https://badgen.net/codecov/c/github/NCAR/xdevbot
    :target: https://codecov.io/gh/NCAR/xdevbot
    :alt: Coverage

.. |License| image:: https://badgen.net/github/license/NCAR/xdevbot?012345
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: License

.. |PyPI| image:: https://badgen.net/pypi/v/xdevbot?label=pypi&012345
    :target: https://pypi.org/project/xdevbot
    :alt: PyPI
