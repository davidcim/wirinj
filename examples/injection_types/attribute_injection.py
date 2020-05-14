from typing import Type

from wirinj import inject, Autowiring, deps, INJECTED


class Feeder:
    pass


class Cat:
    feeder: Feeder = INJECTED

    def __init__(self, color, weight):
        self.color = color
        self.weight = weight


@inject(Autowiring())
def fn(factory: Type[Cat]):
    cat = factory('blue', 12)
    print('cat.feeder:', cat.feeder)


fn()
