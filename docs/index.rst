Welcome to ``alchimia``
=======================

``alchimia`` lets you use most of the `SQLAlchemy-core`_ API with Twisted, it
does not allow you to use the ORM.

Getting started
---------------

.. code-block:: python

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


Get the code
------------

We're on `github`_. Fork us!

.. _`SQLAlchemy-core`: http://docs.sqlalchemy.org/en/latest/core/tutorial.html
.. _`github`: https://github.com/alex/alchimia


Contents
--------

.. toctree::
    :maxdepth: 2

    ddl
    api-reference
    limitations
    contributing
