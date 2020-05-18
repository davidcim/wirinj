from unittest import TestCase

from wirinj import Autowiring, Definitions
from wirinj.core import INJECTED
from wirinj.injector import Injector


class Reality(object):
    pass


class Thing:

    reality: Reality = INJECTED
    cfg = INJECTED
    not_injected = 'ABC'

    def __init__(self, param):
        self.param = param

config = {
    'cfg': 'DEF',
}


class TestInjector(TestCase):

    def test_field_injection(self):

        inj = Injector(Definitions(config), Autowiring())

        thing = inj.get(Thing, 'my-param')
        self.assertIsInstance(thing, Thing)
        self.assertEqual(thing.param, 'my-param')
        self.assertIsInstance(thing.reality, Reality)
        self.assertEqual(thing.not_injected, 'ABC')
        self.assertEqual(thing.cfg, 'DEF')
