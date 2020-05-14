from typing import Type

from wirinj import inject, Autowiring


class Cat:
    def __init__(self, sound):
        pass


@inject(Autowiring())
def fn(cat_factory: Type[Cat]):
    cat = cat_factory('Meow')
    print('cat:', cat)


fn()
