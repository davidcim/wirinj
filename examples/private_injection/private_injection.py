from typing import Type

from wirinj import inject, Autowiring, deps


class Feeder:
    pass


class Cat:
    def __deps__(self, feeder: Feeder):
        self.feeder = feeder

    @deps
    def __init__(self, color, weight):
        self.color = color
        self.weight = weight
        self.fe


@inject(Autowiring())
def fn(factory: Type[Cat]):
    cat = factory('blue', 12)
    print('cat.feeder:', cat.feeder)


fn()
