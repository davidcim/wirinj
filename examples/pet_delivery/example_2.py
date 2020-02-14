import logging
from typing import Type

from examples.pet_delivery.classes import Bob, Vehicle, PetPicker, Pet, Mike, Van, Cat, Truck, Dog
from examples.pet_delivery.defs import pet_defs, vehicle_defs, common_defs
from wirinj import Singleton, Factory, Definitions, inject

world_two_defs = {
    (Bob, Vehicle): Singleton(Van),
    (Bob, PetPicker, Type[Pet]): Factory(Cat),

    (Mike, Type[Vehicle]): Factory(Truck),
    (Mike, PetPicker, Type[Pet]): Factory(Dog),
}

world_two = Definitions(
    pet_defs,
    vehicle_defs,
    common_defs,
    world_two_defs,
)

logging.basicConfig(format='%(message)s', level=logging.INFO)


@inject(world_two)
def do(bob: Bob, mike: Mike):
    bob.deliver(100, 5, False)
    bob.deliver(50, 200, True)

    mike.deliver(20, 1000, True)


do()
