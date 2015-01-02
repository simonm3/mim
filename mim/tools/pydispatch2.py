""" extensions to pydispatch 

    connects signals to callback functions (publish/subscribe model)
"""

from logs import log
from pydispatch.dispatcher import connect, send, disconnect, Any
DEBUG=False

def on(signal=Any, sender=Any, weak=False):
    """ decorator that connects a function to a signal event
        e.g. @on(signalFired)
        note weak=False keeps callback functions alive
        weak references would mean callbacks are garbage collected
    """
    def inner(receiver):
        signal.connect(receiver, sender=sender, weak=weak)
        return receiver
    return inner

class Signal(object):
    """ Defines signal object for use with pydispatch. Adds logging.
    """
    def __init__(self, name=None):
        self.name=name    

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return self.name or u'UNNAMED {0}'.format(hash(self))

    def connect(self, receiver, sender=Any, weak=False):
        """ connect signal to receiver """
        if DEBUG:
            log.debug('Connect {receiver.__module__}.{receiver.__name__} to {self}'.format(**locals()))
        connect(receiver, signal=self, sender=sender, weak=weak)

    def send(self, sender="No sender", *args, **kwargs):
        """ send signal """
        if DEBUG:
            log.debug('Send {self} from {sender}'.format(**locals()))
        send(signal=self, sender=sender, *args, **kwargs)

    def disconnect(receiver, sender=Any, weak=False):
        """ Disconnect receiver from signal """
        if DEBUG:
            log.debug('Disconnect {receiver} from {self}'.format(**locals()))
        disconnect(receiver, signal=self, sender=sender, weak=weak)
