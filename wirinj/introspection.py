from inspect import getfullargspec, FullArgSpec
from typing import Type, Sequence, Callable, Optional

from .core import Arg, NotSet, InjectionType, DEPS_METHOD, InstanceArgs, NotSetType


def is_builtin_cls(annotation) -> [NotSetType, bool]:
    return NotSet if annotation is NotSet else annotation.__module__ == 'builtins'


def get_deps_from_argspec(spec: FullArgSpec) -> Sequence[Arg]:
    result = []

    defaults_idx_base = (0 if spec.defaults is None else len(spec.defaults)) - len(spec.args)
    n = 0
    for i, name in enumerate(spec.args):
        if name == 'self':
            continue
        default_idx = defaults_idx_base + i
        default = spec.defaults[default_idx] if default_idx >= 0 else NotSet
        annotation = spec.annotations.get(name, NotSet)
        result.append(Arg(name, annotation, default))
        n += 1
    return result



def get_func_result(func: Callable) -> Sequence[Arg]:
    assert isinstance(func, Callable), \
        '"{}" must be Callable'.format(func.__name__)
    spec = getfullargspec(func)
    return spec.annotations.get('return', NotSet)


def get_func_args(func: Callable) -> Sequence[Arg]:

    assert isinstance(func, Callable), \
        '"{}" must be Callable'.format(func.__name__)

    spec = getfullargspec(func)
    return get_deps_from_argspec(spec)


def get_method_args(cls, method_name) -> Sequence[Arg]:

    method = getattr(cls, method_name)

    assert method, 'Missing method {1} on class {0}'.format(cls.__name__, method_name)

    assert isinstance(method, Callable), \
        '"{0}.{1}" must be Callable'.format(cls.__name__, method_name)

    spec = getfullargspec(method)
    return get_deps_from_argspec(spec)



def get_class_injection_type(cls) -> InjectionType:
    init_method = getattr(cls, '__init__')

    if not init_method:
        return InjectionType.none

    spec = getfullargspec(init_method)

    try:
        if spec.kwonlyargs and spec.kwonlyargs.index('dependencies') >= 0:
            return InjectionType.deps
    except ValueError:
        pass

    return InjectionType.init


def get_class_deps(cls):
    args = []

    # Base deps
    for base_cls in cls.__bases__:
        if base_cls.__module__ != 'builtins':
            args += get_class_deps(base_cls)

    # Current deps
    method = getattr(cls, DEPS_METHOD, None)
    if method:
        args += get_method_args(cls, DEPS_METHOD)

    return args


def get_class_dependencies(cls) -> Sequence[Arg]:

    injection_type = get_class_injection_type(cls)

    if injection_type == InjectionType.none:
        return ()
    elif injection_type == InjectionType.init:
        return get_method_args(cls, '__init__')
    elif injection_type == InjectionType.deps:
        return get_class_deps(cls)
    else:
        raise ValueError()


def instantiate_class(cls, instance_args: Optional[InstanceArgs] = None, **deps):

    type = get_class_injection_type(cls)

    if instance_args:
        args = instance_args.args
        kwargs = instance_args.kwargs
    else:
        args = ()
        kwargs = {}

    if type == InjectionType.none:
        return cls()
    elif type == InjectionType.init:
        return cls(*args, **{**deps, **kwargs})
    elif type == InjectionType.deps:
        return cls(*args, dependencies=deps, **kwargs)
    else:
        raise ValueError()
