from unittest import TestCase

from typing import Type
from wirinj.definition import Instance, Definitions
from wirinj import Autowiring
from wirinj.decorators import inject


class TestAutowiring(TestCase):

    def test_full_injection_with_autowiring(self):
        class Cat:
            pass

        class Dog:
            pass

        class Horse:
            pass

        deps = {
            Cat: Instance(),
        }

        @inject(Definitions(deps), Autowiring())
        def fn(cat: Cat, dog: Dog, horse_factory: Type[Horse]):
            horse = horse_factory()

            self.assertIsInstance(cat, Cat)
            self.assertIsInstance(dog, Dog)
            self.assertIsInstance(horse, Horse)

        fn()
