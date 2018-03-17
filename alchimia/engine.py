from __future__ import absolute_import, division

from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import StatementError

from twisted._threads import ThreadWorker, AlreadyQuit

from twisted.internet.defer import Deferred, fail
from twisted.python.failure import Failure

from threading import Thread

try:
    from Queue import Queue
except ImportError:
    from queue import Queue


def _threaded_worker():
    def _start_thread(target):
        thread = Thread(target=target)
        thread.daemon = True
        return thread.start()
    return ThreadWorker(_start_thread, Queue())


def _defer_to_worker(deliver, worker, work, *args, **kwargs):
    deferred = Deferred()

    @worker.do
    def container():
        try:
            result = work(*args, **kwargs)
        except BaseException:
            f = Failure()
            deliver(lambda: deferred.errback(f))
        else:
            deliver(lambda: deferred.callback(result))
    return deferred


class TwistedEngine(object):
    def __init__(self, pool, dialect, url, reactor=None,
                 create_worker=_threaded_worker,
                 **kwargs):
        if reactor is None:
            raise TypeError("Must provide a reactor")

        self._engine = Engine(pool, dialect, url, **kwargs)
        self._reactor = reactor
        self._create_worker = create_worker
        self._engine_worker = self._create_worker()

    @classmethod
    def from_sqlalchemy_engine(cls, reactor, engine,
                               create_worker=_threaded_worker):
        # Leaving the existing __init__ in place for compatibility reasons,
        # this is a completely alternate constructor.
        self = cls.__new__(cls)
        self._reactor = reactor
        self._engine = engine
        self._create_worker = create_worker
        self._engine_worker = create_worker()
        return self

    def _defer_to_engine(self, f, *a, **k):
        return _defer_to_worker(self._reactor.callFromThread,
                                self._engine_worker, f, *a, **k)

    @property
    def dialect(self):
        return self._engine.dialect

    @property
    def _has_events(self):
        return self._engine._has_events

    @property
    def _execution_options(self):
        return self._engine._execution_options

    def _should_log_info(self):
        return self._engine._should_log_info()

    def execute(self, *args, **kwargs):
        return (self._defer_to_engine(self._engine.execute, *args, **kwargs)
                .addCallback(TwistedResultProxy, self._defer_to_engine))

    def has_table(self, table_name, schema=None):
        return self._defer_to_engine(
            self._engine.has_table, table_name, schema)

    def table_names(self, schema=None, connection=None):
        if connection is not None:
            connection = connection._connection
        return self._defer_to_engine(
            self._engine.table_names, schema, connection)

    def connect(self):
        worker = self._create_worker()
        return (_defer_to_worker(self._reactor.callFromThread, worker,
                                 self._engine.connect)
                .addCallback(TwistedConnection, self, worker))


class TwistedConnection(object):
    def __init__(self, connection, engine, worker):
        self._connection = connection
        self._engine = engine
        self._cxn_worker = worker

    def _defer_to_cxn(self, f, *a, **k):
        return _defer_to_worker(self._engine._reactor.callFromThread,
                                self._cxn_worker, f, *a, **k)

    def execute(self, *args, **kwargs):
        try:
            return (
                self._defer_to_cxn(self._connection.execute, *args, **kwargs)
                .addCallback(TwistedResultProxy, self._defer_to_cxn)
            )
        except AlreadyQuit:
            return fail(StatementError("This Connection is closed.",
                                       None, None, None))

    def close(self, *args, **kwargs):
        result = self._defer_to_cxn(self._connection.close, *args, **kwargs)
        self._cxn_worker.quit()
        return result

    @property
    def closed(self):
        return self._connection.closed

    def begin(self, *args, **kwargs):
        return (self._defer_to_cxn(self._connection.begin, *args, **kwargs)
                .addCallback(lambda txn: TwistedTransaction(txn, self)))

    def begin_nested(self, *args, **kwargs):
        return (
            self._defer_to_cxn(self._connection.begin_nested, *args, **kwargs)
            .addCallback(lambda txn: TwistedTransaction(txn, self))
        )

    def in_transaction(self):
        return self._connection.in_transaction()


class TwistedTransaction(object):
    def __init__(self, transaction, cxn):
        self._transaction = transaction
        self._cxn = cxn

    def commit(self):
        return self._cxn._defer_to_cxn(self._transaction.commit)

    def rollback(self):
        return self._cxn._defer_to_cxn(self._transaction.rollback)

    def close(self):
        return self._cxn._defer_to_cxn(self._transaction.close)


class TwistedResultProxy(object):
    def __init__(self, result_proxy, deferrer):
        self._result_proxy = result_proxy
        self._deferrer = deferrer

    def fetchone(self):
        return self._deferrer(self._result_proxy.fetchone)

    def fetchall(self):
        return self._deferrer(self._result_proxy.fetchall)

    def scalar(self):
        return self._deferrer(self._result_proxy.scalar)

    def first(self):
        return self._deferrer(self._result_proxy.first)

    def keys(self):
        return self._deferrer(self._result_proxy.keys)

    def close(self):
        return self._deferrer(self._result_proxy.close)

    @property
    def returns_rows(self):
        return self._result_proxy.returns_rows

    @property
    def rowcount(self):
        return self._result_proxy.rowcount

    @property
    def inserted_primary_key(self):
        return self._result_proxy.inserted_primary_key
