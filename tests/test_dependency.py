from unittest import TestCase

from wirinj import Definitions, Injector
from wirinj.decorators import func_inject
from wirinj.definition import CustomSingleton, Singleton, CustomInstance


class TestCustomSingletonDependency(TestCase):

    def test_injection(self):
        class Foo:
            def __init__(self, bar):
                self.bar = bar

        def foo_creator(bar) -> Foo:
            return Foo(bar)

        deps = Definitions({
            'bar': 'Hola',
            Foo: CustomSingleton(foo_creator),
        })

        @func_inject(deps)
        def do(foo: Foo):
            self.assertIsNotNone(foo)
            self.assertIsNotNone(foo.bar)

        do()

class TestCustomInstanceDependency(TestCase):
    def test_get_with_params(self):
        class Baz:
            pass

        class Foo:
            def __init__(self, bar, baz):
                self.bar = bar
                self.baz = baz

        def foo_creator(baz: Baz):
            def creator(bar):
                return Foo(bar, baz)

            return creator

        injector = Injector(Definitions({
            Baz: Singleton(),
            Foo: CustomInstance(foo_creator, True),
        }))

        foo = injector.get(Foo, 'Ping')
        self.assertIs(foo.bar, 'Ping')
        self.assertIsNotNone(foo.baz)


        foo2 = injector.get(Foo, bar='Pong')
        self.assertIs(foo2.bar, 'Pong')
        self.assertIsNotNone(foo2.baz)

        pass
