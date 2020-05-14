from typing import Type

from wirinj import INJECTED, inject, Autowiring, Definitions


class MyService:
    def __str__(self):
        return f'<MyService>'


class MyObject:
    my_service: MyService = INJECTED
    my_config: str = INJECTED

    def __str__(self):
        return f'<MyObject> -> my_config: "{self.my_config}"' \
               f', param: {self.param}, my_service: {self.my_service}'

    def __init__(self, param):
        self.param = param


config = {
    'my_config': 'some conf',
}


# The decorator will inject a dependency into each function parameter
# based on its name and/or annotation type
@inject(Definitions(config), Autowiring())
def do(
        my_service: MyService,
        my_object_factory: Type[MyObject]
):
    print(my_service)

    my_object1 = my_object_factory(10)
    print(my_object1)


# Inject and run it
do()
