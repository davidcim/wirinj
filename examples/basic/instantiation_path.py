from wirinj import inject, Definitions, Instance


class Animal:
    def __init__(self, sound):
        self.sound = sound


class Dog(Animal):
    pass


class Cat(Animal):
    pass


class Cow(Animal):
    pass


defs = {
    Dog: Instance(),
    Cat: Instance(),
    Cow: Instance(),

    (Dog, 'sound'): 'woof',
    (Cat, 'sound'): 'meow',
    'sound': '?',
}


@inject(Definitions(defs))
def fn(cat: Cat, dog: Dog, cow: Cow):
    print('Cat:', cat.sound)
    print('Dog:', dog.sound)
    print('Cow:', cow.sound)


fn()
