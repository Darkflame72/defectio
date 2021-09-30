.. currentmodule:: defectio.base

Cache
-----

Two different cache implementations are available:
  :class:`~defectio.base.cache.Cache`
  :class:`~defectio.base.cache.MutableCache`.

It is recommended to implement the Mutable Cache unless you are sure
that the cache should not be modified by the program. Having a non-mutable
cache is useful if the cache exists in a shared memory space with seperate
proccesses.

Cache
~~~~~

.. autoclass:: Cache
    :members:

MutableCache
~~~~~~~~~~~~

This has all of the same methods as :class:`Cache`, but it is mutable.

.. autoclass:: MutableCache
    :members:
