from unittest import TestCase

from wirinj import Autowiring, deps
from wirinj.core import Injected, InjectHere
from wirinj.injector import Injector


class Reality(object):
    pass


class Thing:

    reality: Reality = InjectHere

    def __init__(self, param):
        self.param = param


class TestInjector(TestCase):

    def test_field_injection(self):

        inj = Injector(Autowiring())

        thing = inj.get(Thing, 'my-param')
        self.assertIsInstance(thing, Thing)
        self.assertEqual(thing.param, 'my-param')
        self.assertIsInstance(thing.reality, Reality)
