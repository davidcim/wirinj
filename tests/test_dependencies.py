from typing import Any
from unittest import TestCase

from wirinj import INJECTED
from wirinj.injector import Injector
from wirinj.definition import Definitions, CustomSingleton, Singleton, CustomInstance
from wirinj.decorators import inject

class TestCustomSingletonDependency(TestCase):

    def test_full_injection(self):
        class Foo:
            def __init__(self, bar):
                self.bar = bar

        def foo_creator(bar) -> Foo:
            return Foo(bar)

        deps = Definitions({
            'bar': 'Hola',
            Foo: CustomSingleton(foo_creator),
        })

        @inject(deps)
        def do(foo: Foo):
            self.assertIsNotNone(foo)
            self.assertIsNotNone(foo.bar)

        do()

class TestCustomInstanceDependency(TestCase):

    def test_custom_instance_with_params(self):
        class Baz:
            pass

        class Foo:
            def __init__(self, bar, baz: Baz = INJECTED):
                self.bar = bar
                self.baz = baz

        def foo_creator(bar, baz: Baz):
            return Foo(bar, baz)

        injector = Injector(Definitions({
            Baz: Singleton(),
            Foo: CustomInstance(foo_creator),
        }))

        foo = injector.get(Foo, 'Ping')
        self.assertIs(foo.bar, 'Ping')
        self.assertIsNotNone(foo.baz)

        foo2 = injector.get(Foo, bar='Pong')
        self.assertIs(foo2.bar, 'Pong')
        self.assertIsNotNone(foo2.baz)

        pass
