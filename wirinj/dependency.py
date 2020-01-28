from typing import Union, Any, Optional, Sequence, Type, Callable

from . import Injector
from .core import Dependency, NotSet, Arg, InjectionType, InstanceArgs, USE_SUBCLASSING_FACTORY
from .introspection import get_method_args, get_class_injection_type, get_class_dependencies, instantiate_class, \
    get_func_args, get_func_result
from .sys import get_subclassing_factory, get_func_factory


class ValueDependency(Dependency):

    def __init__(self, value):
        self.value = value

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
        if USE_SUBCLASSING_FACTORY:
            factory = get_subclassing_factory(self.cls, self.injector.get)
        else:
            factory = get_func_factory(self.cls, self.injector.get)

        return factory


class CustomInstanceDependency(Dependency):

    def __init__(self, func: Callable, wrapper_func: bool = False, cls=None):
        self.func = func
        self.wrapper_func = wrapper_func
        self.cls = cls

    def get_class(self) -> Union[Any, NotSet]:
        if self.cls:
            return self.cls

        return get_func_result(self.func)

    def get_dependencies(self) -> Optional[Sequence[Arg]]:
        args = get_func_args(self.func)
        return args

    def get_instance(self, instance_args: InstanceArgs = None, **deps):
        instance_creation = self.func(**deps)

        if not self.wrapper_func:
            return instance_creation
        else:
            assert isinstance(instance_creation, Callable)
            if instance_args:
                return instance_creation(*instance_args.args, **instance_args.kwargs)
            else:
                return instance_creation()
