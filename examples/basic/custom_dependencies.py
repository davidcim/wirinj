from random import randint

from wirinj import CustomInstance, inject, Definitions


class Cat:
    def __init__(self, color, weight):
        self.color = color
        self.weight = weight

    def __str__(self):
        return 'A {1} pounds {0} cat.'.format(self.color, self.weight)


def create_cat(color):
    return Cat(color, randint(4, 20))


defs = {
    'color': 'blue',
    Cat: CustomInstance(create_cat),
}


@inject(Definitions(defs))
def fn(cat1: Cat, cat2: Cat, cat3: Cat):
    print(cat1)
    print(cat2)
    print(cat3)


fn()
