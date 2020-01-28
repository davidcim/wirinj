from abc import abstractmethod, ABCMeta
from inspect import isabstract
from typing import Sequence, List, Callable, Optional, Dict, Union

from .core import Arg, NotSet, Locator, Dependency, SEPARATOR_OPEN, SEPARATOR_CLOSE
from .dependency import FactoryDependency, InstanceDependency, SingletonWrapper, ValueDependency, \
    CustomInstanceDependency
from .injector import Injector
from .locator import LocatorCache, LocatorChain
from .sys import is_typing_type, get_typing_args


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
                path_item = creation_path[-i-1]
                if not(isinstance(def_item, str) and def_item == path_item.name or def_item == path_item.cls):
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
    def __init__(self, creator: Callable, wrapper_func: bool = False, cls=None):
        self.creator = creator
        self.wrapper_func = wrapper_func
        self.cls = cls

    def create(self, creation_path: List[Arg], injector: Injector):
        return CustomInstanceDependency(self.creator, self.wrapper_func, self.cls)


class CustomSingleton(DependencyBuilder):
    def __init__(self, creator: Callable, wrapper_func: bool = False, cls=None):
        self.creator = creator
        self.wrapper_func = wrapper_func
        self.cls = cls

    def create(self, creation_path: List[Arg], injector: Injector):
        return SingletonWrapper(CustomInstanceDependency(self.creator, self.wrapper_func, self.cls))

CustomFactory = CustomSingleton


class Factory(DependencyBuilder):
    def __init__(self, cls=None):
        self.cls = cls

    def create(self, creation_path: List[Arg], injector: Injector):
        if self.cls is None:
            last = creation_path[-1]
            assert is_typing_type(last.cls),\
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
            assert isinstance(last.cls, type),\
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



class DefinitionLocator(Locator):
    def __init__(self, definitions: Dict):
        self.finder = DefinitionFinder(definitions)
        self.injector = None  # type: Optional[Injector]

    def initialize(self, injector):
        self.injector = injector

    def get(self, creation_path: List[Arg]) -> Optional[Dependency]:
        assert self.injector is not None

        _ , value = self.finder(creation_path)
        if value is NotSet:
            return None
        if isinstance(value, DependencyBuilder):
            return value.create(creation_path, self.injector)
        else:
            return ValueDependency(value)


class AutowiringReportBase(metaclass=ABCMeta):

    @abstractmethod
    def add(self, line):
        pass

    @abstractmethod
    def get(self):
        pass

class NullAutowiringReport(AutowiringReportBase):

    def add(self, line):
        pass

    def get(self):
        return ''


class AutowiringReport(AutowiringReportBase):

    def __init__(self):
        self.lines = []

    def add(self, line):
        self.lines.append(line)

    def get(self):
        if not self.lines:
            return ''

        lines = ''
        for line in self.lines:
            lines += '    {},\n'.format(line)
        return '{0}\n{1}\n\n{2}({{\n{3}}}),\n{4}'.format(
            SEPARATOR_OPEN,
            'Autowiring report:',
            DefinitionLocator.__name__,
            lines,
            SEPARATOR_CLOSE,
        )


class Autowiring(Locator):

    def __init__(self, report: Optional[AutowiringReport] = None):
        self.report = report if report else NullAutowiringReport()
        self.singletons = {}

    def initialize(self, injector):
        self.injector = injector

    def get(self, creation_path: Sequence[Arg]) -> Optional[Dependency]:
        arg = creation_path[-1]

        if arg.cls is NotSet:
            return None

        try:
            return self.singletons[arg.cls]
        except KeyError:
            pass

        # Something annotated with Type[] is a factory
        if is_typing_type(arg.cls):
            type_cls = get_typing_args(arg.cls)
            self.report.add('Type[{}]: Factory()'.format(type_cls.__name__))
            factory_dep = SingletonWrapper(FactoryDependency(type_cls, self.injector))
            self.singletons[arg.cls] = factory_dep
            return factory_dep

        # If a non abstract class
        elif not isabstract(arg.cls):

            # With a name, this comes probably from a function arg and therefore it is presumably a singleton
            if arg.name:
                self.report.add('{}: Singleton()'.format(arg.cls.__name__))
                singleton_dep = SingletonWrapper(InstanceDependency(arg.cls))
                self.singletons[arg.cls] = singleton_dep
                return singleton_dep

            # Without a name, this comes probably from a factory call and therefore it is presumably an instance
            else:
                self.report.add('{}: Instance()'.format(arg.cls.__name__))
                return InstanceDependency(arg.cls)
        return None


class Definitions(Locator):
    def __init__(self, *args: Union[Locator, dict], cached=True):

        assert len(args), 'You have to provide at least one dependency locator'

        locators = []
        for arg in args:
            if isinstance(arg, Locator):
                locators.append(arg)

            elif isinstance(arg, dict):
                locators.append(DefinitionLocator(arg))

        uncached = LocatorChain(locators) if len(locators) > 1 else locators[0]
        self.locator = LocatorCache(uncached) if cached else uncached

    def initialize(self, injector):
        self.locator.initialize(injector)

    def get(self, creation_path: Sequence[Arg]) -> Optional[Dependency]:
        return self.locator.get(creation_path)
