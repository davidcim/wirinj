from wirinj import inject, Definitions, Instance, Singleton, Factory


class Cat:
    pass


class Dog:
    pass


defs = {
    'sound': 'Meow',
    Cat: Instance(),
    Dog: Singleton(),
    'cat_factory': Factory(Cat),
}


@inject(Definitions(defs))
def fn(cat1: Cat, cat2: Cat, dog: Dog, sound, cat_factory):
    print('sound:', sound)
    print('cat1:', cat1)
    print('cat2:', cat2)
    print('cat1 = cat2:', cat1 is cat2)
    print('dog:', dog)

    cat3 = cat_factory()
    print('cat3:', cat3)


fn()
