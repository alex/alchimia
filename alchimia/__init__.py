from __future__ import absolute_import, division

from alchimia.strategy import TWISTED_STRATEGY
from alchimia.engine import TwistedEngine

wrap_engine = TwistedEngine.from_sqlalchemy_engine
del TwistedEngine

__all__ = [
    "TWISTED_STRATEGY",
    "wrap_engine",
]
