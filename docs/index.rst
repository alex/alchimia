Welcome to ``alchimia``
=======================

``alchimia`` lets you use most of the
:ref:`SQLAlchemy-core <sqlalchemy:core>` API with Twisted, it does
not allow you to use the ORM.

Getting started
---------------

.. code-block:: python

    from alchimia import TWISTED_STRATEGY

    from sqlalchemy import create_engine

    from twisted.internet.defer import inlineCallbacks
    from twisted.internet.task import react


    @inlineCallbacks
    def main(reactor):
        # The important parts here are ``reactor=reactor`` and
        # ``strategy=TWISTED_STRATEGY``
        engine = create_engine(
            "sqlite://", reactor=reactor, strategy=TWISTED_STRATEGY
        )
        # Let's query for the answer to life, the universe, and everything
        result = yield engine.execute("SELECT 42")
        answer = yield result.scalar()
        print("The answer to life, the universe, and everything is: %s" % answer)

    if __name__ == "__main__":
        react(main, [])


Contents
--------

.. toctree::
    :maxdepth: 2

    ddl
    api-reference
    limitations
    contributing
