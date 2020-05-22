from abc import abstractmethod, ABCMeta
from logging import getLogger
from typing import Optional, Union, Sequence, Any, TypeVar

import wirinj
from .tools import get_cls_name

logger = getLogger(wirinj.__name__)

SEPARATOR_OPEN = '--------------- ' + wirinj.__name__ + ' ---------------'
SEPARATOR_CLOSE = '--------------------------------------'

signature_injection = False
DEPS_METHOD = '__deps__'

init_arg_injection = False
INJECTION_ARG = '_dependencies'

QUERY_WRAPPED_METHOD = '_query_wrapped_method'


class FactoryStrategy:
    SUBCLASS = 1
    FUNCTION = 2

factory_strategy = FactoryStrategy.SUBCLASS


class NotSetType(type):
    def __str__(self):
        return 'NotSet'


class NotSet(metaclass=NotSetType):
    pass


class FunctionArgs:
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


INJECTED = TypeVar('INJECTED')


InjectionClauses = [INJECTED]

class Arg:
    def __init__(self, name: Optional[str], cls: Union[NotSetType, Any] = NotSet,
                 default: Union[NotSetType, Any] = NotSet):
        """
        Arg is the representation of a function argument in the context of dependency injection.
        @param name: Name of the argument.
        @param cls: Type annotation of the argument.
        @param default: Default value for the argument.
        """
        self.name = name
        self.cls = cls
        self.default = default

    def __str__(self) -> str:
        return "{}{}{}".format(
            str('' if self.name is None else self.name),
            '' if self.cls is NotSet else ':{}'.format(get_cls_name(self.cls)),
            '' if self.default is NotSet else '={}'.format(str(self.default)),
        )

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((hash(self.name), hash(self.cls), hash(self.default)))


class Dependency(metaclass=ABCMeta):

    def get_class(self) -> Union[Any, NotSet]:
        return NotSet

    def get_dependencies(self) -> Optional[Sequence[Arg]]:
        return None

    @abstractmethod
    def get_instance(self, instance_args: FunctionArgs = None, **deps):
        pass


class Locator(metaclass=ABCMeta):

    def initialize(self, injector):
        pass

    @abstractmethod
    def get(self, creation_path: Sequence[Arg]) -> Optional[Dependency]:
        pass


def filter_direct_args(arg_list: Sequence[Arg], args, kwargs):
    result = []
    i = -1
    for arg in arg_list:

        i += 1

        if i < len(args):
            continue

        if arg.name in kwargs and arg.default != kwargs[arg.name]:
            continue

        result.append(arg)

    return result


def join_arg_sequences(*arg_sequences: Sequence[Arg]):
    result = []
    index = {}
    for arg_sequence in reversed(arg_sequences):
        for arg in arg_sequence:
            if index.get(arg.name):
                continue
            index[arg.name] = True
            result += arg
    return result
