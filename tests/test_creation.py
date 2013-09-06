import sqlalchemy

from twisted.trial import unittest

from alchimia.engine import TwistedEngine, TwistedConnection

from .doubles import FakeThreadedReactor


def create_engine():
    return sqlalchemy.create_engine(
        "sqlite://", strategy="twisted", reactor=FakeThreadedReactor()
    )


class TestEngineCreation(object):
    def test_simple_create_engine(self):
        engine = sqlalchemy.create_engine(
            "sqlite://", strategy="twisted", reactor=FakeThreadedReactor()
        )
        assert isinstance(engine, TwistedEngine)


class TestConnect(unittest.TestCase):
    def test_engine_connect(self):
        engine = create_engine()
        d = engine.connect()
        connection = self.successResultOf(d)
        assert isinstance(connection, TwistedConnection)


class TestConnection(unittest.TestCase):
    def test_execute(self):
        engine = create_engine()
        d = engine.execute("SELECT 42")
        result = self.successResultOf(d)
        d = result.scalar()
        assert self.successResultOf(d) == 42
