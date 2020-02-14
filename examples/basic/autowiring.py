from typing import Type
from wirinj import Instance, inject, Definitions, Autowiring


class Cat:
    pass


class Dog:
    pass


class Horse:
    pass


defs = {
    Cat: Instance(),
}


@inject(Definitions(defs), Autowiring())
def fn(cat: Cat, dog: Dog, horse_factory: Type[Horse]):
    print(cat.__class__.__name__)
    print(dog.__class__.__name__)
    horse = horse_factory()
    print(horse.__class__.__name__)


fn()
