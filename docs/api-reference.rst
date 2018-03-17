API Reference
=============

Many of these classes are missing methods from the SQLALchemy API. We encourage
you to :doc:`file bugs </contributing>` in those cases.

.. currentmodule:: alchimia

.. function:: wrap_engine(reactor, engine, create_worker=...)

   This returns a :py:class:`alchimia.engine.TwistedEngine`.

   The main entry-point to alchimia.  To be used like so::

        from sqlalchemy import create_engine
        from alchimia import wrap_engine
        from twisted.internet import reactor

        underlying_engine = create_engine("sqlite://")
        twisted_engine = wrap_engine(reactor, engine)

   - ``reactor`` - the Twisted reactor to use with the created
     ``TwistedEngine``.

   - ``engine`` - the underlying :py:class:`sqlalchemy.engine.Engine`

   - ``create_worker`` - The object that will coordinate concurrent blocking
       work behind the scenes.  The default implementation, if nothing is
       passed, is one which will use a threadpool where each Connection is tied
       to an individual thread.

       More precisely, this is a callable that is expected to return an object
       with 2 methods, ``do(work)`` (expected to call the 0-argument ``work``
       callable in a thread), and ``quit()``, expected to stop any future work
       from occurring.  It may be useful to stub out the default threaded
       implementation for testing purposes.

.. currentmodule:: alchimia.engine


.. class:: TwistedEngine

    Mostly like :class:`sqlalchemy.engine.Engine` except some of the methods
    return ``Deferreds``.

    .. method:: __init__(pool, dialect, url, reactor=..., create_worker=...)

       This constructor is invoked if ``TwistedEngine`` is created via
       ``create_engine(..., reactor=reactor, strategy=TWISTED_STRATEGY)``
       rather than called directly.  New applications should prefer
       :py:func:`alchimia.wrap_engine`.  However, ``create_engine`` relays its
       keyword arguments, so the ``reactor`` and ``create_worker`` arguments
       have the same meaning as they do in :py:func:`alchimia.wrap_engine`.

    .. classmethod:: from_sqlalchemy_engine(reactor, engine, create_worker=...)

       This is the implementation of ``alchimia.wrap_engine``.

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

    .. method:: begin_nested()

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
