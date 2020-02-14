from typing import Type
from wirinj import Instance, inject, Definitions, Autowiring, AutowiringReport


class Cat:
    pass


class Dog:
    pass


class Horse:
    pass


deps = {
    Cat: Instance(),
}

report = AutowiringReport()


@inject(Definitions(deps), Autowiring(report))
def fn(cat: Cat, dog: Dog, horse_factory: Type[Horse]):
    print(cat.__class__.__name__)
    print(dog.__class__.__name__)
    horse = horse_factory()
    print(horse.__class__.__name__)


fn()

print(report.get())
