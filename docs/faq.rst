Frequently Asked Questions
===========================

This is a list of Frequently Asked Questions regarding using ``defectio`` and its extension modules. Feel free to suggest a
new question or submit one via pull requests.

General
---------

General questions around the library belong here.

Where can I find usage examples?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example code can be found in the `examples folder <https://github.com/Darkflame72/defectio/tree/main/examples>`_
in the repository.

Why is it called ``defectio``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Defectio is latin for "Revolt" and I personally thought it sounded nice.

Coroutines
----------

Questions regarding coroutines and asyncio belong here.

What is a coroutine?
~~~~~~~~~~~~~~~~~~~~~~

A |coroutine_link|_ is a function that must be invoked with ``await`` or ``yield from``. When Python encounters an ``await`` it stops
the function's execution at that point and works on other things until it comes back to that point and finishes off its work.
This allows for your program to be doing multiple things at the same time without using threads or complicated
multiprocessing.

**If you forget to await a coroutine then the coroutine will not run. Never forget to await a coroutine.**

Where can I use ``await``\?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can only use ``await`` inside ``async def`` functions and nowhere else.

What does "blocking" mean?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In asynchronous programming a blocking call is essentially all the parts of the function that are not ``await``. Do not
despair however, because not all forms of blocking are bad! Using blocking calls is inevitable, but you must work to make
sure that you don't excessively block functions. Remember, if you block for too long then your bot will freeze since it has
not stopped the function's execution at that point to do other things.

If logging is enabled, this library will attempt to warn you that blocking is occurring with the message:
``Heartbeat blocked for more than N seconds.``
See :doc:`logging` for details on enabling logging.

A common source of blocking for too long is something like :func:`time.sleep`. Don't do that. Use :func:`asyncio.sleep`
instead. Similar to this example: ::

    # bad
    time.sleep(10)

    # good
    await asyncio.sleep(10)

Use, use the :doc:`aiohttp <aio:index>` library which is installed on the side with this library. To make http requests.

Consider the following example: ::

    # bad
    r = requests.get('http://aws.random.cat/meow')
    if r.status_code == 200:
        js = r.json()
        await channel.send(js['file'])

    # good
    async with aiohttp.ClientSession() as session:
        async with session.get('http://aws.random.cat/meow') as r:
            if r.status == 200:
                js = await r.json()
                await channel.send(js['file'])
