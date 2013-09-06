from sqlalchemy import create_engine

from twisted.trial import unittest

from alchimia.engine import TwistedEngine, TwistedConnection

from .doubles import FakeThreadedReactor


class TestEngineCreation(object):
    def test_simple_create_engine(self):
        engine = create_engine("sqlite://", strategy="twisted", reactor=FakeThreadedReactor())
        assert isinstance(engine, TwistedEngine)


class TestConnect(unittest.TestCase):
    def test_engine_connect(self):
        engine = create_engine("sqlite://", strategy="twisted", reactor=FakeThreadedReactor())
        d = engine.connect()
        connection = self.successResultOf(d)
        assert isinstance(connection, TwistedConnection)
