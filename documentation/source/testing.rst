Testing
=======

``epowcore`` aims to work with large and complex energy system models.
These models are used to perform simulations whose results might be relevant for real-world decision-making.
Finding errors in large models is difficult and time consuming.
Thus, we need automated tests to create trust in the conversion process.

Setup
-----

.. note:: `PF Documentation - PFD Import <https://www.digsilent.de/en/faq-reader-powerfactory/how-to-import-export-pfd-files-by-using-script.html>`_ might be interesting for implementing import of PFD files.

1. Setup the entire project as described in :doc:`/setup`.
2. PowerFactory: Import the projects in ``tests/models/powerfactory``.
3. Run tests with ``pytest`` on the root directory of the project.

.. note:: 

    Some tests are really slow (*looking at you, Matlab*) and might not be necessary to run every time.
    We place these cases in the ``tests_slow`` folder. If you just want to run the "fast" tests, run ``pytest tests/``.


The following command yields more insights into the testing procedure:

.. code-block:: shell

    pytest --cov=epowcore --cov-context=test tests/ tests_slow/; coverage html --show-contexts

- ``--cov=epowcore``: calculate the test coverage of the given module
- ``--cov-context=test``: track which test case executes which line (context)
- ``coverage html --show-contexts``: create an html representation of the coverage and display the context
- ``tests/ tests_slow/``: the test folders to include


General Guidelines
------------------

- The file/folder structure of the tests should follow the structure in the source folder.
- Create **real** unit tests: test each function/method individually -- mock if necessary. Make it clear what is tested where.


Tips & Tricks
-------------

Handling Singletons
^^^^^^^^^^^^^^^^^^^

In some places, ``epowcore`` uses Singletons to make features available globally.
An example for this would be the ``Configuration`` class that provides access to the user-editable configuration files.

.. warning:: 

    Singleton instances stay intact between different test case runs! Thus, it is a good idea to clear them before/after every run.

In some cases, you might want to manipulate a singleton in order to get reliable test results.
For example, you could manipulate the ``Configuration`` singleton to always return a value that you define in your test.
Not cleaning up singletons would result in other test cases working with this manipulated ``Configuration`` as well.

An easy way to clean up singletons can be implemented in the ``setUp`` and ``tearDown`` methods of the ``TestCase``:

.. code-block:: python

    def setUp(self) -> None:
        Singleton._instances = {}

    # or

    def tearDown(self) -> None:
        Singleton._instances = {}

These methods empty the dictionary that keeps the ``Singleton`` instances before and after every test case, respectively.
This mechanism can also be used to place manipulated objects for testing purposes in the ``Singleton`` dictionary:

.. code-block:: python

    Singleton._instances = {
        Configuration: my_test_config,
    }


Mocking
^^^^^^^

A powerful mechanism, especially for unit testing is `mocking <https://docs.python.org/3.10/library/unittest.mock.html>`_.
This technique enables replacing objects/classes that the code under test depends on with **mock objects** whose behavior can be defined specifically for the test.
This breaks strong code interdependence and allows us to test smaller pieces of code individually.

In the following test code snippet, the ``patch`` decorator inserts a ``Configuration`` mock object into the test method.
The test then places this mock ``Configuration`` as the global ``Singleton`` and defines its behavior:


.. code-block:: python

    import unittest
    from unittest.mock import patch

    class DataStructureTest(unittest.TestCase):

        @patch("epowcore.generic.configuration.Configuration")
        def test_base_mva_fb2(self, mock_config):
            Singleton._instances = {
                Configuration: mock_config,
            }
            mock_config.get_default.return_value = 1000.0

A good starting point to learn more about mocking can be found here: https://docs.python.org/3.10/library/unittest.mock-examples.html