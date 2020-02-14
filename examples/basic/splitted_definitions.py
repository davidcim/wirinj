from typing import Type

from wirinj import Instance, Factory, Definitions, inject


class Cat:
    pass


defs1 = {
    Cat: Instance(),
    Type[Cat]: Factory()
}


class Engine:
    pass


defs2 = {
    Engine: Instance(),
    Type[Engine]: Factory()
}


@inject(Definitions(defs1, defs2))
def fn(cat_factory: Type[Cat], engine_factory: Type[Engine]):
    cat = cat_factory()
    engine = engine_factory()

    print('cat:', cat)
    print('engine:', engine)


fn()
