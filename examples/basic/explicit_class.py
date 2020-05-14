from wirinj import Singleton, inject, Definitions


class Pet:
    pass


class Cat(Pet):
    pass


class Dog(Pet):
    pass


defs = {
    'cat': Singleton(Cat),
    Pet: Singleton(Dog),
}


@inject(Definitions(defs))
def fn(cat, pet: Pet):
    print('cat is a', cat.__class__.__name__)
    print('pet is a', pet.__class__.__name__)


fn()
