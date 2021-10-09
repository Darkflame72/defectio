.. _defectio-api-events:

Event Reference
---------------

This section outlines the different types of events listened by :class:`Client`.

There are two ways to register an event, the first way is through the use of
:meth:`Client.event`. The second way is through subclassing :class:`Client` and
overriding the specific events. For example: ::

    import defectio

    class MyClient(defectio.Client):
        async def on_message(self, message):
            if message.author == self.user:
                return

            if message.content.startswith('$hello'):
                await message.channel.send('Hello World!')

If an event handler raises an exception, :func:`on_error` will be called
to handle it, which defaults to print a traceback and ignoring the exception.

.. warning::

    All the events must be a |coroutine_link|_. If they aren't, then you might get unexpected
    errors. In order to turn a function into a coroutine they must be ``async def``
    functions.

.. function:: on_ready()

    Called when the client is done preparing the data received from Revolt. Usually after login is successful.

    .. warning::

        This function is not guaranteed to be the first event called.
        Likewise, this function is **not** guaranteed to only be called
        once. This library implements reconnection logic and thus will
        end up calling this event whenever a RESUME request fails.

.. function:: on_error(event, *args, **kwargs)

    Usually when an event raises an uncaught exception, a traceback is
    printed to stderr and the exception is ignored. If you want to
    change this behaviour and handle the exception for whatever reason
    yourself, this event can be overridden. Which, when done, will
    suppress the default action of printing the traceback.

    The information of the exception raised and the exception itself can
    be retrieved with a standard call to :func:`sys.exc_info`.

    If you want exception to propagate out of the :class:`Client` class
    you can define an ``on_error`` handler consisting of a single empty
    :ref:`raise statement <py:raise>`. Exceptions raised by ``on_error`` will not be
    handled in any way by :class:`Client`.

    :param event: The name of the event that raised the exception.
    :type event: :class:`str`

    :param args: The positional arguments for the event that raised the
        exception.
    :param kwargs: The keyword arguments for the event that raised the
        exception.

.. function:: on_message(message)

    Called when a message is received.

    :param message: The message that was received.
    :type message: :class:`Message`

    .. note::

        This event is called for every message received, including
        messages sent by the client itself.

        If you want to filter out messages sent by the client, you
        can use the ``message.author == client.user`` check.

        If you want to filter out messages sent by other users, you
        can use the ``message.author != client.user`` check.

.. function:: on_raw_message_update(message)

    Called when a message is updated.

    :param message: The message that was updated.
    :type message: :class:`dict`

.. function:: on_message_update(old_message, message)

    Called when a message is updated.

    :param old_message: The original message if it exists in the cache.
    :type old_message: :class:`Message`

    :param message: The message that was updated.
    :type message: :class:`Message`
