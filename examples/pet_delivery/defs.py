from typing import Type

from .classes import Mike, Vehicle, Bob, Car, PetPicker, PetLoader, Pet, Bird, Van, Dog, VehicleBuilder, \
    Truck, Engine, Plate, Wheel, Container, Cat
from wirinj import Definitions, Factory, Singleton, Instance

pet_defs = {
    Dog: Instance(),
    Cat: Instance(),
    Bird: Instance(),

    (Dog, 'sound'): 'Woof',
    (Dog, 'weight'): 10,

    (Cat, 'sound'): 'Meow',
    (Cat, 'weight'): 5,

    (Bird, 'sound'): 'Chirp',
    (Bird, 'weight'): 0.1,
}


vehicle_defs = {
    Engine: Instance(),
    Plate: Instance(),
    Wheel: Instance(),
    Container: Instance(),

    Type[Engine]: Factory(),
    Type[Plate]: Factory(),
    Type[Wheel]: Factory(),
    Type[Container]: Factory(),

    VehicleBuilder: Singleton(),

    (Engine, 'mount_sound'): 'RRRRoarrr',
    (Plate, 'mount_sound'): 'plaf',
    (Wheel, 'mount_sound'): 'pffff',
    (Container, 'mount_sound'): 'BLOOOOM',

    Car: Instance(),
    (Car, 'max_load_weight'): 10,
    (Car, 'recipe'): {
        'engines': 1,
        'plates': 6,
        'wheels': 4,
    },

    Van: Instance(),
    (Van, 'max_load_weight'): 50,
    (Van, 'recipe'): {
        'engines': 1,
        'plates': 8,
        'wheels': 4,
    },

    Truck: Instance(),
    (Truck, 'max_load_weight'): 200,
    (Truck, 'recipe'): {
        'engines': 1,
        'plates': 20,
        'wheels': 12,
        'container': 1,
    },
}

common_defs = {
    PetPicker: Singleton(),
    PetLoader: Singleton(),

    Bob: Singleton(),
    Mike: Singleton(),
}

world_one_defs = {
    (Bob, Vehicle): Singleton(Car),
    (Bob, PetPicker, Type[Pet]): Factory(Bird),

    (Mike, Type[Vehicle]): Factory(Van),
    (Mike, PetPicker, Type[Pet]): Factory(Cat),
}

world_two_defs = {
    (Bob, Vehicle): Singleton(Van),
    (Bob, PetPicker, Type[Pet]): Factory(Cat),

    (Mike, Type[Vehicle]): Factory(Truck),
    (Mike, PetPicker, Type[Pet]): Factory(Dog),
}

world_one = Definitions(
    pet_defs,
    vehicle_defs,
    common_defs,
    world_one_defs,
)

world_two = Definitions(
    pet_defs,
    vehicle_defs,
    common_defs,
    world_two_defs,
)
