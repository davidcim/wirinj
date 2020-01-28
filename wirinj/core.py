from abc import abstractmethod, ABCMeta
from enum import Enum
from logging import getLogger
from typing import Optional, Union, Any, Sequence

import wirinj
from .sys import get_cls_name

logger = getLogger(wirinj.__name__)


SEPARATOR_OPEN  = '--------------- wirinj ---------------'
SEPARATOR_CLOSE = '--------------------------------------'

DEPS_METHOD = '__deps__'


USE_SUBCLASSING_FACTORY = True

class NotSetType(type):
    def __str__(self):
        return 'NotSet'


class NotSet(metaclass=NotSetType):
    pass


class InjectionType(Enum):
    init = 1
    deps = 2
    none = 3


class InstanceArgs:
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


class Arg:
    def __init__(self, name: Optional[str], cls: Union[NotSetType, Any] = NotSet, default: Union[NotSetType, Any] = NotSet):
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
    def get_instance(self, instance_args: InstanceArgs = None, **deps):
        pass


class Locator(metaclass=ABCMeta):

    def initialize(self, injector):
        pass

    @abstractmethod
    def get(self, creation_path: Sequence[Arg]) -> Optional[Dependency]:
        pass


def filter_explicit_args(arg_list: Sequence[Arg], args, kwargs):
    result = []
    for i, arg in enumerate(arg_list):
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
