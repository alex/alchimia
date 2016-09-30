from twisted.internet.interfaces import IReactorThreads
from twisted._threads import IWorker, AlreadyQuit

from zope.interface import implementer


@implementer(IReactorThreads)
class FakeThreadedReactor(object):
    def callFromThread(self, f, *args, **kwargs):
        return f(*args, **kwargs)


@implementer(IWorker)
class ImmediateWorker(object):

    def __init__(self):
        self._quitted = False

    def do(self, work):
        if self._quitted:
            raise AlreadyQuit()
        work()

    def quit(self):
        if self._quitted:
            raise AlreadyQuit()
        self._quitted = True
