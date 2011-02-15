"""
Corruptor classes: classes that encapsulate the noise process for the DAE
training criterion.
"""
import numpy
import theano
from theano import tensor

theano.config.warn.sum_div_dimshuffle_bug = False
floatX = theano.config.floatX
sharedX = lambda X, name : theano.shared(numpy.asarray(X, dtype=floatX), name=name)
if 0:
    print 'WARNING: using SLOW rng'
    RandomStreams = tensor.shared_randomstreams.RandomStreams
else:
    import theano.sandbox.rng_mrg
    RandomStreams = theano.sandbox.rng_mrg.MRG_RandomStreams

class Corruptor(object):
    """
    A corruptor object is allocated in the same fashion as other
    objects in this file, with a 'conf' dictionary (or object
    supporting __getitem__) containing relevant hyperparameters.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def alloc(cls, conf, rng=None):
        if not hasattr(rng, 'randn'):
            rng = numpy.random.RandomState(rng)
        self = cls()
        seed = int(rng.randint(2**30))
        self.s_rng = RandomStreams(seed)
        self.conf = conf

    def corrupted(self, inputs):
        """Symbolic expression denoting the corrupted inputs."""
        raise NotImplementedError()

class BinomialCorruptor(Corruptor):
    """
    A binomial corruptor sets inputs to 0 with probability
    0 < `corruption_level` < 1.
    """
    def corrupted(self, inputs):
        return [
            self.s_rng.binomial(
                size=inp.shape,
                n=1,
                p=1 - self.conf['corruption_level'],
                dtype=floatX
            ) * inp
        for inp in inputs]

class GaussianCorruptor(Corruptor):
    """
    A Gaussian corruptor transforms inputs by adding zero
    mean isotropic Gaussian noise with standard deviation
    `corruption_level`.
    """
    def corrupted(self, inputs):
        return [
            self.s_rng.normal(
                size=inp.shape,
                avg=0,
                std=self.conf['corruption_level'],
                dtype=floatX
            ) + inp
        for inp in inputs]

