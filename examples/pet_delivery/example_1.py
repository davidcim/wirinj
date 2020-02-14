import logging
from typing import Type

from examples.pet_delivery.classes import Bob, Vehicle, Car, PetPicker, Pet, Bird, Mike, Van, Cat
from examples.pet_delivery.defs import pet_defs, vehicle_defs, common_defs
from wirinj import Singleton, Factory, Definitions, inject

world_one_defs = {
    (Bob, Vehicle): Singleton(Car),
    (Bob, PetPicker, Type[Pet]): Factory(Bird),

    (Mike, Type[Vehicle]): Factory(Van),
    (Mike, PetPicker, Type[Pet]): Factory(Cat),
}

world_one = Definitions(
    pet_defs,
    vehicle_defs,
    common_defs,
    world_one_defs,
)

logging.basicConfig(format='%(message)s', level=logging.INFO)


@inject(world_one)
def do(bob: Bob, mike: Mike):
    bob.deliver(100, 5, False)
    bob.deliver(50, 200, True)

    mike.deliver(20, 1000, True)


do()
