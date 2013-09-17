import sqlalchemy
from sqlalchemy.engine import RowProxy

from twisted.trial import unittest

from alchimia import TWISTED_STRATEGY
from alchimia.engine import TwistedEngine, TwistedConnection

from .doubles import FakeThreadedReactor


def create_engine():
    return sqlalchemy.create_engine(
        "sqlite://", strategy=TWISTED_STRATEGY, reactor=FakeThreadedReactor()
    )


class TestEngineCreation(object):
    def test_simple_create_engine(self):
        engine = sqlalchemy.create_engine(
            "sqlite://",
            strategy=TWISTED_STRATEGY,
            reactor=FakeThreadedReactor()
        )
        assert isinstance(engine, TwistedEngine)


class TestConnect(unittest.TestCase):
    def test_engine_connect(self):
        engine = create_engine()
        d = engine.connect()
        connection = self.successResultOf(d)
        assert isinstance(connection, TwistedConnection)


class TestConnection(unittest.TestCase):
    def test_engine_execute(self):
        engine = create_engine()
        d = engine.execute("SELECT 42")
        result = self.successResultOf(d)
        d = result.scalar()
        assert self.successResultOf(d) == 42

    def test_connection_execute(self):
        engine = create_engine()
        d = engine.connect()
        conn = self.successResultOf(d)
        d = conn.execute("SELECT 42")
        result = self.successResultOf(d)
        d = result.scalar()
        assert self.successResultOf(d) == 42

    def test_fetchone(self):
        engine = create_engine()
        d = engine.execute("SELECT 42")
        result = self.successResultOf(d)
        d = result.fetchone()
        row = self.successResultOf(d)
        assert isinstance(row, RowProxy)
        assert row[0] == 42

    def test_fetchall(self):
        engine = create_engine()
        d = engine.execute("SELECT 10")
        result = self.successResultOf(d)
        d = result.fetchall()
        rows = self.successResultOf(d)
        assert len(rows) == 1
        assert rows[0][0] == 10
