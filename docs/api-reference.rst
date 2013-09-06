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

.. class:: TwistedConnection

    Mostly like :class:`sqlalchemy.engine.Connection` except some of the
    methods return ``Deferreds``.


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
