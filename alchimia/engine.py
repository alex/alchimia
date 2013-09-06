from sqlalchemy.engine.base import Engine

from twisted.internet.threads import deferToThreadPool


class TwistedEngine(object):
    def __init__(self, pool, dialect, url, reactor=None, **kwargs):
        if reactor is None:
            raise TypeError("Must provide a reactor")

        super(TwistedEngine, self).__init__()
        self._engine = Engine(pool, dialect, url, **kwargs)
        self._reactor = reactor

    def _defer_to_thread(self, f, *args, **kwargs):
        tpool = self._reactor.getThreadPool()
        return deferToThreadPool(self._reactor, tpool, f, *args, **kwargs)

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

    def connect(self):
        d = self._defer_to_thread(self._engine.connect)
        d.addCallback(TwistedConnection)
        return d


class TwistedConnection(object):
    def __init__(self, connection):
        super(TwistedConnection, self).__init__()
        self._connection = connection
