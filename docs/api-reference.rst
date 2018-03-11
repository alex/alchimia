API Reference
=============

Many of these classes are missing methods from the SQLALchemy API. We encourage
you to :doc:`file bugs </contributing>` in those cases.

.. currentmodule:: alchimia.engine


.. class:: TwistedEngine

    Mostly like :class:`sqlalchemy.engine.Engine` except some of the methods
    return ``Deferreds``.

    .. method:: __init__(pool, dialect, url, reactor=..., create_worker=...,
                         customize_sub_engine=...)

       ``TwistedEngine`` is normally created via ``create_engine(...,
       reactor=reactor, strategy=TWISTED_STRATEGY)`` rather than called
       directly.  However, ``create_engine`` relays its keyword arguments, so
       three of the keyword arguments here may be of interest to applications:

       - ``reactor`` - the Twisted reactor to use with this ``TwistedEngine``.
         This should always be explicitly passed to ``create_engine``.

       - ``create_worker`` - a callable that will return an object with 2
         methods, ``do(work)`` (expected to call the 0-argument ``work``
         callable in a thread), and ``quit()``, expected to stop any future
         work from occurring.  It may be useful to stub out the default
         threaded implementation for testing purposes.

       - ``customize_sub_engine`` - A callable that will take the *underlying*
         SQLAlchemy engine when it is created, in order to allow application
         code to customize it.  This is intended to enable event-hook access,
         particularly to facilitate debugging and driver-specific configuration
         or workarounds `like this
         <http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl>`_.
         However, please be aware that this has some implementation
         limitations:

         1. Any callable passed as ``customize_sub_engine`` will be run in a
            threadpool thread, not the main thread, as it is run where the
            Engine is created.  This means it's safe to use APIs on the engine,
            but it is *not* safe to call Twisted or reactor APIs in either this
            callable or in any event-listeners registered on the underlying
            engine itself, which will also be run in the database threadpool
            appropriate to the connection that the event is occurring on.

         2. While currently all Alchimia drivers are simply threaded wrappers
            around existing synchronous SQLAlchemy drivers, this argument may
            become a no-op or an error with any future natively-asynchronous
            drivers.

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

    .. method:: close()

	Like the SQLAlchemy method of the same name, it releases the
	resources used and releases the underlying DB connection.

    .. attribute:: returns_rows

        Like the SQLAlchemy attribute of the same name.

    .. attribute:: rowcount

        Like the SQLAlchemy attribute of the same name.

    .. attribute:: inserted_primary_key

        Like the SQLAlchemy attribute of the same name.
