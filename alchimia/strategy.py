from sqlalchemy.engine.strategies import DefaultEngineStrategy

from alchimia.engine import TwistedEngine


class TwistedEngineStrategy(DefaultEngineStrategy):
    """
    An EngineStrategy for use with Twisted. Many of the Engine's methods will
    return Deferreds instead of results. See the documentation of
    ``TwistedEngine`` for more details.
    """

    name = "twisted"
    engine_cls = TwistedEngine
