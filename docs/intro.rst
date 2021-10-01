Introduction
==============

This is the documentation for defectio, a library for Python to aid
in creating applications that utilise the Revolt API.

Prerequisites
---------------

defectio works with Python 3.8 or higher. Support for earlier versions of Python
is not provided. Python 2.7 or lower is not supported. Python 3.7 or lower is not supported.


.. _installing:

Installing
-----------

You can get the library directly from PyPI: ::

    python3 -m pip install -U defectio

If you are using Windows, then the following should be used instead: ::

    py -3 -m pip install -U defectio

Remember to check your permissions!

Virtual Environments
~~~~~~~~~~~~~~~~~~~~~

Sometimes you want to keep libraries from polluting system installs or use a different version of
libraries than the ones installed on the system. You might also not have permissions to install libraries system-wide.
For this purpose, Python comes with a concept called "Virtual Environments" to
help maintain these separate versions.

A more in-depth tutorial can be found at :doc:`py:tutorial/venv`.

However, for the quick and dirty:

1. Go to your project's working directory:

    .. code-block:: shell

        $ cd your-bot-source
        $ python3 -m venv bot-env

2. Activate the virtual environment:

    .. code-block:: shell

        $ source bot-env/bin/activate

    On Windows you activate it with:

    .. code-block:: shell

        $ bot-env\Scripts\activate.bat

3. Use pip like usual:

    .. code-block:: shell

        $ pip install -U defectio

Congratulations. You now have a virtual environment all set up.

Basic Concepts
---------------

defectio revolves around the concept of :ref:`events <defectio-api-events>`.
An event is something you listen to and then respond to. For example, when a message
happens, you will receive an event about it that you can respond to.

Here is a quick example to showcase how events work:

.. code-block:: python3

    import defectio

    class MyClient(defectio.Client):
        async def on_ready(self):
            print(f'Logged on as {self.user}!')

        async def on_message(self, message):
            print(f'Message from {message.author}: {message.content}')

    client = MyClient()
    client.run('my token goes here')
