
Python Driver for Oracle NoSQL Database Cloud Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This document is for developers of the Python SDK for the Oracle NoSQL Database
Cloud Service. Developers are those who need to modify source and examples,
build and run tests and examples, and build documentation.


===============
Getting Started
===============
Clone the repository and Install dependencies.

1. Make sure that Python is installed on your system, at least version 2.7.
2. Install pip if it is not installed, follow
   the `pip installation instructions <https://pip.pypa.io/en/stable/installing>`_.
3. Clone the repository and install development dependencies

    ::

     git clone https://github.com/oracle/nosql-python-sdk.git
     cd nosql-python-sdk
     pip install -r requirements.txt

Running Tests and Examples
==========================

During development the unit tests and examples run against a local CloudSim server,
which can run on the local machine. See
`Download the Oracle NoSQL Cloud Simulator <https://docs.oracle.com/pls/topic/lookup?ctx=en/cloud/paas/nosql-cloud&id=CSNSD-GUID-3E11C056-B144-4EEA-8224-37F4C3CB83F6>`_ to download and start the Cloud Simulator.

Tests and examples have settings that can be changed based on environment.
Test settings are in test/parameters.py. Refer to the comments in the tests and
examples for details. The default values will use a Cloud Simulator instance
that is running on its default settings of localhost:8080.

All tests require that your PYTHONPATH be set to the development tree:

 $ export PYTHONPATH=<path-to-nosql-python-sdk>/nosql-python-sdk/src:$PYTHONPATH

Run Unit Tests
--------------

    1. Modify <path-to-repo>/test/parameters.py to suit your environment. The
       comments in that file tells you how to modify the settings.
    2. With the CloudSim server running, start testing.

      .. code-block::

        $ cd <path-to-repo>/test
        $ python -m unittest discover -p '*.py' (Run all the tests)
        $ python <testcase>.py (Run individual test)

      You can also run a test case using the following command

      .. code-block::

            $ python -m unittest <testfile>.<testclass>.<testname>
            e.g.
            $ python -m unittest put.TestPut.testPutNoVersionWithMatchVersion

Run Examples
------------

    1. Set PYTHONPATH to point to the development tree.
       $ export PYTHONPATH=<path-to-nosql-python-sdk>/nosql-python-sdk/src:$PYTHONPATH
    2. Modify <path-to-repo>/examples/parameters.py to suit your environment.
       The comments in that file tells you how to modify the settings.
    3. With the CloudSim running, run a test

      .. code-block::

       $ cd <path-to-repo>/examples
       $ python multi_data_ops.py

Building Documentation
======================

The documentation build depends on sphinx (http://sphinx-doc.org/install.html),
sphinx-automodapi, and sphinx_rtd_theme. They should have been installed
per the instructions above.

.. code-block::

  $ cd <path-to-repo>/docs
  $ make html

Documentation is built into <path-to-repo>/docs/_build.
If public api classes are modified it may be necessary to modify, add, or remove
files in <path-to-repo>/docs/api as well as modifying relevant files in the docs
directory.
