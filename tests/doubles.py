from twisted.internet.interfaces import IReactorThreads

from zope.interface import implementer


@implementer(IReactorThreads)
class FakeThreadedReactor(object):
    def getThreadPool(self):
        return FakeThreadPool()

    def callFromThread(self, f, *args, **kwargs):
        return f(*args, **kwargs)


class FakeThreadPool(object):
    def callInThreadWithCallback(self, cb, f, *args, **kwargs):
        cb(True, f(*args, **kwargs))
