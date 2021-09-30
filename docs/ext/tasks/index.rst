.. currentmodule:: defectio.ext.tasks

``defectio.ext.tasks`` -- asyncio.Task helpers
====================================================

One of the most common operations when making a bot is having a loop run in the background at a specified interval. This pattern is very common but has a lot of things you need to look out for:

- How do I handle :exc:`asyncio.CancelledError`?
- What do I do if the internet goes out?
- What is the maximum number of seconds I can sleep anyway?

The goal of this defectio extension is to abstract all these worries away from you.

.. toctree::
  :maxdepth: 1

  recipes
  api
