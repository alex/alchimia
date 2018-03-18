alchimia
========

``alchimia`` lets you use most of the SQLAlchemy-core API with Twisted, it does
not allow you to use the ORM.

Getting started
---------------

.. code:: python

    from alchimia import wrap_engine

    from sqlalchemy import (
        create_engine, MetaData, Table, Column, Integer, String
    )
    from sqlalchemy.schema import CreateTable

    from twisted.internet.defer import inlineCallbacks
    from twisted.internet.task import react


    @inlineCallbacks
    def main(reactor):
        engine = wrap_engine(reactor, create_engine("sqlite://"))

        metadata = MetaData()
        users = Table("users", metadata,
            Column("id", Integer(), primary_key=True),
            Column("name", String()),
        )

        # Create the table
        yield engine.execute(CreateTable(users))

        # Insert some users
        yield engine.execute(users.insert().values(name="Jeremy Goodwin"))
        yield engine.execute(users.insert().values(name="Natalie Hurley"))
        yield engine.execute(users.insert().values(name="Dan Rydell"))
        yield engine.execute(users.insert().values(name="Casey McCall"))
        yield engine.execute(users.insert().values(name="Dana Whitaker"))

        result = yield engine.execute(users.select(users.c.name.startswith("D")))
        d_users = yield result.fetchall()
        # Print out the users
        for user in d_users:
            print("Username: %s" % user[users.c.name])
	# Queries that return results should be explicitly closed to
	# release the connection
        result.close()

    if __name__ == "__main__":
        react(main, [])

Documentation
-------------

The documentation is all on `Read the Docs`_.

.. _`Read the Docs`: https://alchimia.readthedocs.io/

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
  Luckily, many of these methods have alternate spelling. `The docs`_ call these
  out in more detail.

.. _`The docs`: https://alchimia.readthedocs.io/en/latest/limitations/
