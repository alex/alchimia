from twisted.internet.interfaces import IReactorThreads
from twisted.python.failure import Failure

from zope.interface import implementer


@implementer(IReactorThreads)
class FakeThreadedReactor(object):
    def getThreadPool(self):
        return FakeThreadPool()

    def callFromThread(self, f, *args, **kwargs):
        return f(*args, **kwargs)


class FakeThreadPool(object):
    def callInThreadWithCallback(self, cb, f, *args, **kwargs):
        try:
            result = f(*args, **kwargs)
        except Exception as e:
            cb(False, Failure(e))
        else:
            cb(True, result)
