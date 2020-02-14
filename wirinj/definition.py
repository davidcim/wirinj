from abc import abstractmethod
from typing import List, Callable, Optional, Dict

from .core import Arg, NotSet, Locator, Dependency
from .dependencies import FactoryDependency, InstanceDependency, SingletonWrapper, ValueDependency, \
    CustomInstanceDependency
from .injector import Injector
from .tools import is_typing_type, get_typing_args


class DefinitionFinder:
    def __init__(self, definitions: Dict):
        assert isinstance(definitions, dict)
        self.definitions = definitions

    def __call__(self, creation_path: List[Arg]):

        result_key = None
        result_value = None
        def_len = 0

        for key, value in self.definitions.items():
            definition = key if isinstance(key, list) or isinstance(key, tuple) else (key,)

            if len(definition) > len(creation_path):
                continue

            if len(definition) <= def_len:
                continue

            match = True
            for i, def_item in enumerate(reversed(definition)):
                path_item = creation_path[-i - 1]
                if not (isinstance(def_item, str) and def_item == path_item.name or def_item == path_item.cls):
                    match = False
                    break
            if match:
                result_key = key
                result_value = value
                def_len = len(definition)

        return (NotSet, NotSet) if def_len == 0 else (result_key, result_value)


class DependencyBuilder:

    @abstractmethod
    def create(self, creation_path: List[Arg], injector: Injector):
        pass


class CustomInstance(DependencyBuilder):
    def __init__(self, creator: Callable, cls=None):
        self.creator = creator
        self.cls = cls

    def create(self, creation_path: List[Arg], injector: Injector):
        if not self.cls and creation_path and creation_path[-1].cls is not NotSet:
            cls = creation_path[-1].cls
        else:
            cls = self.cls
        return CustomInstanceDependency(self.creator, cls)


class CustomSingleton(DependencyBuilder):
    def __init__(self, creator: Callable, cls=None):
        self.creator = creator
        self.cls = cls

    def create(self, creation_path: List[Arg], injector: Injector):
        return SingletonWrapper(CustomInstanceDependency(self.creator, self.cls))


CustomFactory = CustomSingleton


class Factory(DependencyBuilder):
    def __init__(self, cls=None):
        self.cls = cls

    def create(self, creation_path: List[Arg], injector: Injector):
        if self.cls is None:
            last = creation_path[-1]
            assert is_typing_type(last.cls), \
                'Factory without params needs Type[YourClass] as last element in the definition path'
            cls = get_typing_args(last.cls)
        else:
            cls = self.cls

        return SingletonWrapper(FactoryDependency(cls, injector))


class Instance(DependencyBuilder):
    def __init__(self, cls=None):
        self.cls = cls

    def create(self, creation_path: List[Arg], injector: Injector):
        if self.cls is None:
            last = creation_path[-1]
            assert isinstance(last.cls, type), \
                'Instance without params needs YourClass as last element in the definition path'
            cls = last.cls
        else:
            cls = self.cls

        return InstanceDependency(cls)


class Singleton(DependencyBuilder):
    def __init__(self, cls=None):
        self.cls = cls

    def create(self, creation_path: List[Arg], injector: Injector):
        if self.cls is None:
            last = creation_path[-1]
            assert isinstance(last.cls, type), \
                'Singleton without params needs YourClass as last element in the definition path'
            cls = last.cls
        else:
            cls = self.cls

        return SingletonWrapper(InstanceDependency(cls))


class Definitions(Locator):
    def __init__(self, *definitions: Dict):

        assert len(definitions), 'You have to provide at least one definition dict'

        defs = {}
        for df in definitions:
            defs = {**defs, **df}

        self.finder = DefinitionFinder(defs)
        self.injector = None  # type: Optional[Injector]

    def initialize(self, injector):
        self.injector = injector

    def get(self, creation_path: List[Arg]) -> Optional[Dependency]:
        assert self.injector is not None

        _, value = self.finder(creation_path)
        if value is NotSet:
            return None
        if isinstance(value, Dependency):
            return value
        if isinstance(value, DependencyBuilder):
            return value.create(creation_path, self.injector)
        else:
            return ValueDependency(value)
