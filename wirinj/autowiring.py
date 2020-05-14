from abc import ABCMeta, abstractmethod
from inspect import isabstract
from typing import Optional, Sequence

from .definition import Definitions
from .core import Dependency, Arg, Locator, SEPARATOR_OPEN, SEPARATOR_CLOSE, NotSet
from .dependencies import SingletonWrapper, FactoryDependency, InstanceDependency
from .introspect import is_builtin_cls
from .tools import is_typing_type, get_typing_args, is_typing_clause


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
            Definitions.__name__,
            lines,
            SEPARATOR_CLOSE,
        )


def is_autowireable_cls(cls):
    return not isabstract(cls) and not is_builtin_cls(cls) and not is_typing_clause(cls)


class Autowiring(Locator):

    def __init__(self, report: Optional[AutowiringReport] = None, use_singletons=True):
        self.report = report if report else NullAutowiringReport()
        self.singletons = {}
        self.use_singletons = use_singletons

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
            if not is_autowireable_cls(type_cls):
                return None
            self.report.add('Type[{}]: Factory()'.format(type_cls.__name__))
            factory_dep = SingletonWrapper(FactoryDependency(type_cls, self.injector))
            self.singletons[arg.cls] = factory_dep
            return factory_dep

        # If is a valid class to be autowired
        elif is_autowireable_cls(arg.cls):

            # With a name, this comes probably from a function arg and therefore it is presumably a singleton
            if arg.name and self.use_singletons:
                self.report.add('{}: Singleton()'.format(arg.cls.__name__))
                singleton_dep = SingletonWrapper(InstanceDependency(arg.cls))
                self.singletons[arg.cls] = singleton_dep
                return singleton_dep

            # Without a name, this comes probably from a factory call and therefore it is presumably an instance
            else:
                self.report.add('{}: Instance()'.format(arg.cls.__name__))
                return InstanceDependency(arg.cls)
        return None
