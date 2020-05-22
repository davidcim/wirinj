from typing import Union, Any, Optional, Sequence, Type, Callable

from .core import Dependency, NotSet, Arg, FunctionArgs, factory_strategy, FactoryStrategy
from .injector import Injector
from .introspect import get_class_dependencies, instantiate_class, \
    get_func_args, get_func_result
from .tools import get_subclassing_factory, get_func_factory


class ValueDependency(Dependency):

    def __init__(self, value):
        self.value = value

    def get_class(self) -> Union[Any, NotSet]:
        return self.value.__class__

    def get_instance(self, instance_args=None, **deps):
        return self.value


class InstanceDependency(Dependency):

    def __init__(self, cls):
        self.cls = cls

    def get_class(self) -> Union[Any, NotSet]:
        return self.cls

    def get_dependencies(self) -> Optional[Sequence[Arg]]:
        return get_class_dependencies(self.cls)

    def get_instance(self, instance_args=None, **deps):
        return instantiate_class(self.cls, instance_args, **deps)


class SingletonWrapper(Dependency):

    def __init__(self, dependency: Dependency):
        self.dependency = dependency
        self.instance = None

    def get_class(self) -> Union[Any, NotSet]:
        return self.dependency.get_class()

    def get_dependencies(self) -> Optional[Sequence[Arg]]:
        if self.instance:
            return ()
        return self.dependency.get_dependencies()

    def get_instance(self, instance_args=None, **deps):
        if self.instance:
            assert instance_args is None or not instance_args.args and not instance_args.kwargs
        else:
            self.instance = self.dependency.get_instance(instance_args, **deps)
        return self.instance


class FactoryDependency(Dependency):

    def __init__(self, cls, injector: Injector):
        self.cls = cls
        self.injector = injector

    def get_class(self) -> Union[Any, NotSet]:
        return Type[self.cls]

    def get_dependencies(self) -> Optional[Sequence[Arg]]:
        return []

    def get_instance(self, instance_args=None, **deps):
        if factory_strategy == FactoryStrategy.SUBCLASS:
            factory = get_subclassing_factory(self.cls, self.injector.get)
        else:
            factory = get_func_factory(self.cls, self.injector.get)

        return factory


class CustomInstanceDependency(Dependency):

    def __init__(self, func: Callable, cls=None):
        self.func = func
        self.cls = cls

    def get_class(self) -> Union[Any, NotSet]:
        if self.cls:
            return self.cls

        return get_func_result(self.func)

    def get_dependencies(self) -> Optional[Sequence[Arg]]:
        args = get_func_args(self.func)
        return args

    def get_instance(self, instance_args: FunctionArgs = None, **deps):

        if instance_args:
            return self.func(*instance_args.args, **{**deps, **instance_args.kwargs})
        else:
            return self.func(**deps)
