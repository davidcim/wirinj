from random import randint
from typing import Type

from wirinj import CustomInstance, Factory, inject, Definitions


class Cat:
    def __init__(self, name, color=None, weight=None):
        self.name = name
        self.color = color
        self.weight = weight

    def __str__(self):
        return f'{self.name} is a {self.color} pounds {self.weight} cat.'


def create_cat(name, color):
    return Cat(name, color, randint(4, 20))


defs = {
    'color': 'black',
    Cat: CustomInstance(create_cat),
    Type[Cat]: Factory(),
}


@inject(Definitions(defs))
def fn(factory: Type[Cat]):
    cat = factory('Tom')
    print(cat)
    cat2 = factory('Sam')
    print(cat2)


fn()
