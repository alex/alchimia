API Reference
=============

Many of these classes are missing methods from the SQLALchemy API. We encourage
you to :doc:`file bugs </contributing>` in those cases.

.. currentmodule:: alchimia.engine


.. class:: TwistedEngine

    Mostly like :class:`sqlalchemy.engine.Engine` except some of the methods
    return ``Deferreds``.

    .. method:: connect()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with a :class:`TwistedConnection`.

    .. method:: execute(*args, **kwargs)

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with a :class:`TwistedResultProxy`.

    .. method:: has_table(table_name, schema=None)

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with the result.

    .. method:: table_names(schema=None, connection=None)

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with the result.


.. class:: TwistedConnection

    Mostly like :class:`sqlalchemy.engine.Connection` except some of the
    methods return ``Deferreds``.

    .. method:: execute(*args, **kwargs)

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with a :class:`TwistedResultProxy`.

    .. method:: close()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires when the connection has been closed.

    .. attribute:: closed

        Like the SQLAlchemy attribute of the same name.

    .. method:: begin()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with a :class:`TwistedTransaction`.

    .. method:: in_transaction()

        Like the SQLAlchemy method of the same name.


.. class:: TwistedTransaction

    Mostly like :class:`sqlalchemy.engine.Transaction` except some of the
    methods return ``Deferreds``.

    .. method:: commit()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires when the transaction has been committed.

    .. method:: rollback()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires when the transaction has been rolled back.

    .. method:: closed()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires when the transaction has been closed.


.. class:: TwistedResultProxy

    Mostly like :class:`sqlalchemy.engine.ResultProxy` except some of the
    methods return ``Deferreds``.

    .. method:: fetchone()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with a row.

    .. method:: fetchall()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with a list of rows.

    .. method:: scalar()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with the scalar value.

    .. method:: first()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with the scalar value.

    .. method:: keys()

        Like the SQLAlchemy method of the same name, except returns a
        ``Deferred`` which fires with the scalar value.

    .. attribute:: returns_rows

        Like the SQLAlchemy attribute of the same name.

    .. attribute:: rowcount

        Like the SQLAlchemy attribute of the same name.

    .. attribute:: inserted_primary_key

        Like the SQLAlchemy attribute of the same name.
