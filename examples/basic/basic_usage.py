from typing import Type

from wirinj import Definitions, Instance, Singleton, Factory, INJECTED, inject


class MyService:
    def __str__(self):
        return f'<{self.__class__.__name__}>'


class MyObject:
    my_service: MyService = INJECTED
    my_config: str = INJECTED

    def __str__(self):
        return f'<{self.__class__.__name__}> -> my_config: "{self.my_config}", param: {self.param}, my_service: {self.my_service}'

    def __init__(self, param):
        self.param = param


# Wiring definitions
defs = {
    'my_config': 'Some config',
    MyService: Singleton(),
    MyObject: Instance(),
    Type[MyObject]: Factory(),
}


# The decorator will inject a dependency on each function parameter based on its name and/or annotation type
@inject(Definitions(defs))
def do(
        my_service: MyService,
        my_object_factory: Type[MyObject]
):
    print('my_service = {}'.format(my_service))

    my_object1 = my_object_factory(10)
    print('my_object1 = {}'.format(my_object1))


# Inject and run it
do()
