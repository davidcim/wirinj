from logging import getLogger
from typing import Type, Dict, List

from wirinj import deps

logger = getLogger(__name__)


class Pet:
    def __deps__(self, sound: str, weight):
        self.sound = sound
        self.weight = weight

    @deps
    def __init__(self, gift_wrapped):
        self.gift_wrapped = gift_wrapped

    def cry(self):
        return self.sound.lower() if self.gift_wrapped else self.sound.upper()


class Cat(Pet):
    pass


class Dog(Pet):
    pass


class Bird(Pet):
    pass


class Part:
    def __deps__(self, mount_sound):
        self.mount_sound = mount_sound

    @deps
    def __init__(self):
        pass

    def mount(self):
        return self.mount_sound


class Engine(Part):
    pass


class Plate(Part):
    pass


class Wheel(Part):
    pass


class Container(Part):
    pass


class VehicleBuilder:

    def __deps__(self,
                 engine_factory: Type[Engine],
                 plate_factory: Type[Plate],
                 wheel_factory: Type[Wheel],
                 container_factory: Type[Container],
                 ):
        self.engine_factory = engine_factory
        self.plate_factory = plate_factory
        self.wheel_factory = wheel_factory
        self.container_factory = container_factory

    @deps
    def __init__(self):
        pass

    def build(self, recipe: Dict):
        parts = []  # type: List[Part]
        parts += [self.engine_factory() for _ in range(recipe.get('engines', 0))]
        parts += [self.plate_factory() for _ in range(recipe.get('plates', 0))]
        parts += [self.wheel_factory() for _ in range(recipe.get('wheels', 0))]
        parts += [self.container_factory() for _ in range(recipe.get('containers', 0))]

        mounting = ''
        for part in parts:
            mounting += ' ' + part.mount()

        return mounting


class Vehicle:
    def __deps__(self, builder: VehicleBuilder, recipe: Dict, max_load_weight):
        self.builder = builder
        self.recipe = recipe
        self.max_load_weight = max_load_weight

    @deps
    def __init__(self):
        self.pets = []
        self.build()

    def go(self, miles):
        logger.info('{} goes {} miles'.format(self.__class__.__name__, miles))

    def come_back(self):
        logger.info('{} commes back'.format(self.__class__.__name__))

    def build(self):
        logger.info('{} is built: {}'.format(
            self.__class__.__name__,
            self.builder.build(self.recipe)
        ))

    def get_available_load(self):
        return self.max_load_weight - sum(pet.weight for pet in self.pets)


class Car(Vehicle):
    pass


class Van(Vehicle):
    pass


class Truck(Vehicle):
    pass


class PetLoader:

    def upload(self, pets: List[Pet], vehicle: Vehicle):
        info = 'Uploading to the {}:'.format(vehicle.__class__.__name__.lower())
        while pets:
            pet = pets.pop()
            if vehicle.get_available_load() >= pet.weight:
                vehicle.pets.append(pet)
                info += ' ' + pet.__class__.__name__
            else:
                pets.append(pet)
                break
        logger.info(info)

    def download(self, vehicle):
        logger.info('{} pets delivered'.format(len(vehicle.pets)))
        vehicle.pets = []


class PetPicker:

    def __deps__(self, pet_store: Type[Pet]):
        self.pet_store = pet_store

    @deps
    def __init__(self):
        # raise Exception('HORROR!!!!')
        pass

    def pick(self, qty, gift_wrapped):
        info = 'Picking pets up: '
        pets = []
        for _ in range(qty):
            pet = self.pet_store(gift_wrapped)
            info += ' ' + pet.cry()
            pets.append(pet)
        logger.info(info)
        return pets


class PetDeliveryPerson:

    @deps
    def __init__(self):
        pass

    def deliver(self, pet_qty, miles, gift_wrapped):
        pass


class Bob(PetDeliveryPerson):
    """Bob builds a car and deliver pets in his vehicle repeating the route several times."""

    def __deps__(self, vehicle: Vehicle, pet_picker: PetPicker, pet_loader: PetLoader):
        self.vehicle = vehicle
        self.pet_picker = pet_picker
        self.pet_loader = pet_loader

    def deliver(self, pet_qty, miles, gift_wrapped):
        # Pick up pets
        pets = self.pet_picker.pick(pet_qty, gift_wrapped)

        # Bob owns one vehicle only
        while pets:
            self.pet_loader.upload(pets, self.vehicle)
            self.vehicle.go(miles)
            self.pet_loader.download(self.vehicle)
            self.vehicle.come_back()


class Mike(PetDeliveryPerson):
    """Mike builds several autonomous vehicles and use them to deliver the pets all together"""

    def __deps__(self, vehicle_factory: Type[Vehicle], pet_picker: PetPicker, pet_loader: PetLoader):
        self.vehicle_factory = vehicle_factory
        self.pet_picker = pet_picker
        self.pet_loader = pet_loader

    @deps
    def __init__(self):
        super().__init__()
        self.vehicles = []  # type: List[Vehicle]

    def get_vehicle(self):
        if self.vehicles:
            return self.vehicles.pop()
        else:
            return self.vehicle_factory()

    def park_vehicles(self, vehicles):
        self.vehicles += vehicles

    def deliver(self, pet_qty, miles, gift_wrapped):

        # Pick up pets
        pets = self.pet_picker.pick(pet_qty, gift_wrapped)

        # Get vehicles and upload them
        vehicles = []
        while pets:
            vehicle = self.get_vehicle()
            vehicles.append(vehicle)
            self.pet_loader.upload(pets, vehicle)

        # Go
        for vehicle in vehicles:
            vehicle.go(miles)

        # Deliver pets
        for vehicle in vehicles:
            self.pet_loader.download(vehicle)

        # Come back
        for vehicle in vehicles:
            vehicle.come_back()

        # Park
        self.park_vehicles(vehicles)
