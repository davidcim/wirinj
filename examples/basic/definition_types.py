from random import randint
from typing import Type

from wirinj import Singleton, Instance, Factory, CustomInstance, inject, Definitions


class House:
    pass


class Cat:
    pass


class Dog:
    pass


def dog_builder():
    """ Custom instantiation """
    dog = Dog()
    dog.random = randint(50, 100)
    return dog


defs = {
    House: Singleton(),
    Cat: Instance(),
    Type[Cat]: Factory(),
    Dog: CustomInstance(dog_builder),
    Type[Dog]: Factory(),
}


@inject(Definitions(defs))
def fn(house: House, cat_factory: Type[Cat], dog_factory: Type[Dog]):
    cat = cat_factory()
    dog = dog_factory()

    print('house:', house)
    print('cat:', cat)
    print('dog:', dog)


fn()
