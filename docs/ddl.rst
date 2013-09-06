DDL
===

Because of some of the limitations in the SQLAlchemy API, it's not possible to
create tables using :py:meth:`sqlalchemy.schema.Table.create` or
:py:meth:`sqlalchemy.MetaData.create_all`. Luckily, SQLAlchemy provides an API
that still makes it possible to create tables and perform other DDL operations.

Instead of:

.. code:: python

    users = Table("users", metadata,
        Column("id", Integer(), primary_key=True),
        Column("name", String()),
    )

    users.create(engine)

or

.. code:: python

    metadata.create_all()

You can use:

.. code:: python

    from sqlalchemy.schema import CreateTable

    d = engine.execute(CreateTable(users))
