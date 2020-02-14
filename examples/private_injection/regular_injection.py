from typing import Type

from wirinj import inject, Autowiring


class Feeder:
    pass


class Cat:
    def __init__(self, color, weight, feeder: Feeder = None):
        self.color = color
        self.weight = weight
        self.feeder = feeder


@inject(Autowiring())
def fn(factory: Type[Cat]):
    cat = factory('blue', 12)
    print('cat.feeder:', cat.feeder)


fn()
