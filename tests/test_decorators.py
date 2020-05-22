import logging
from io import StringIO
from typing import Type
from unittest import TestCase

from examples.pet_delivery.classes import Mike
from examples.pet_delivery.defs import world_one
from wirinj import Autowiring, Definitions
from wirinj.core import signature_injection, init_arg_injection, INJECTED
from wirinj.decorators import inject, deps


class Reality:
    pass


class Thing:

    reality: Reality = INJECTED

    def __init__(self, param):
        self.param = param


class Obj:
    def __deps__(self, dependency):
        # This is never executed. Makes work IDE inspections for signature injection.
        self.dependency = dependency

    @deps
    def __init__(self, param):
        self.param = param


class TestDeps(TestCase):

    def test_arg_init_injection(self):
        obj = Obj(10, _dependencies={'dependency': 20})
        self.assertEqual(obj.dependency, 20)
        self.assertEqual(obj.param, 10)

    def test_factory_with_arguments(self):
        @inject(Autowiring())
        def fn(factory: Type[Thing]):
            thing = factory(10)
            self.assertIsInstance(thing, Thing)
            self.assertIsInstance(thing.reality, Reality)

        fn()

    def test_init_dependency(self):
        @inject(Definitions({'param': 10}), Autowiring())
        def fn(thing: Thing):
            self.assertIsInstance(thing, Thing)
            self.assertIsInstance(thing.reality, Reality)
            self.assertIs(thing.param, 10)

        fn()

    def test_injection_on_class_and_subclass(self):
        class Qux:
            pass

        class Foo:
            pass

        class Bar:
            foo: Foo = INJECTED
            foo2: Foo = INJECTED

        class Baz(Bar):
            qux: Qux = INJECTED

        @inject(Autowiring())
        def do(baz: Baz):
            self.assertIsInstance(baz.foo, Foo)
            self.assertIsInstance(baz.foo2, Foo)
            self.assertIsInstance(baz.qux, Qux)
            self.assertIs(baz.foo, baz.foo2)

        do()


class TestInject(TestCase):
    def test_inject_full_pet_delivery_example(self):
        log = StringIO()
        logging.basicConfig(stream=log, level=logging.INFO, format='%(message)s')

        @inject(world_one)
        def do(mike: Mike):
            mike.deliver(100, 5, False)

        do()

        log_str = log.getvalue()
        self.assertMultiLineEqual(
            log_str,
            'Picking pets up:  MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\n',
            'Mismatch in output of test_classes',
        )
