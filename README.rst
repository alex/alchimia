alchimia
========

``alchimia`` lets you use most of the SQLAlchemy-core API with Twisted.

Getting started
---------------

.. code:: python

    import alchimia

    from sqlalchemy import create_engine

    from twisted.internet.defer import inlineCallbacks


    @inlineCallbacks
    def main(reactor):
        engine = create_engine("sqlite://", reactor=reactor, strategy="twisted")
        # Let's query for the answer to life, the universe, and everything
        result = yield engine.execute("SELECT 42")
        print("The answer to life, the universe, and everythign is: %s" % (yield result.scalar()))


Limitations
-----------

There are some limitations to ``alchimia's`` ability to expose the SQLAlchemy
API.

* Some methods simply haven't been implemented yet. If you file a bug, we'll
  implement them! See ``CONTRIBUTING.rst`` for more info.
* Some methods in SQLAlchemy either have no return value, or don't have a
  return value we can control. Since most of the ``alchimia`` API is predicated
  on returning ``Deferred`` instances which fire with the underlying SQLAlchemy
  instances, it is impossible for us to wrap these methods in a useful way.
  Luckily, many of these methods have alternate spelling. The docs call these
  out in more detail.
