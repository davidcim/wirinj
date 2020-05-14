from typing import Type

from wirinj import Instance, Factory, Definitions, inject, INJECTED


class Cat:
    sound: str = INJECTED
    weight: float = INJECTED


config = {
    'sound': 'meow',
    'weight': 5,
}

wiring = {
    Cat: Instance(),
    Type[Cat]: Factory()
}


@inject(Definitions(config, wiring))
def fn(cat_factory: Type[Cat]):
    cat = cat_factory()

    print(f'Cat: {cat.sound}, {cat.weight}')


fn()
