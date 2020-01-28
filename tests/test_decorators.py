import logging
from io import StringIO

from unittest import TestCase

from wirinj import Definitions
from wirinj.decorators import func_inject, inject
from wirinj.definition import Autowiring
from tests.example_classes import Mike, Engine
from tests.example_definitions import world_one_deps


class DecoratorsTest(TestCase):
    def test_func_inject(self):
        engine = Engine(dependencies={'mount_sound': 'Brrrooommm'})
        self.assertEqual(engine.mount_sound, 'Brrrooommm')

    def test_inject(self):
        log = StringIO()
        logging.basicConfig(stream=log, level=logging.INFO, format='%(message)s')

        @func_inject(world_one_deps)
        def do(mike: Mike):
            mike.deliver(100, 5, False)

        do()

        log_str = log.getvalue()
        self.assertMultiLineEqual(
            log_str,
            'Picking pets up:  MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW MEOW\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan is built:  RRRRoarrr plaf plaf plaf plaf plaf plaf plaf plaf pffff pffff pffff pffff\nUploading to the van: Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\nVan goes 5 miles\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\n10 pets delivered\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\nVan commes back\n',
            'Mismatch in output of test_classes',
        )

    def test_double_inject_on_subclass(self):
        class Qux:
            pass

        class Foo:
            pass

        class Bar:

            def __deps__(self, foo: Foo, foo2: Foo, **_):
                pass

            @inject
            def __init__(self):
                pass

        class Baz(Bar):

            def __deps__(self, qux: Qux, **_):
                pass

            @inject
            def __init__(self):
                super().__init__()

        @func_inject(Definitions(Autowiring()))
        def do(baz: Baz):
            self.assertIsNotNone(baz.foo)
            self.assertIsNotNone(baz.foo2)
            self.assertIsNotNone(baz.qux)
            self.assertIs(baz.foo, baz.foo2)
        do()
