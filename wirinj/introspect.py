from inspect import getfullargspec, FullArgSpec
from typing import Sequence, Callable, Optional

from .core import Arg, NotSet, InjectionType, DEPS_METHOD, InstanceArgs, NotSetType, DEPENDENCIES_ARG, \
    QUERY_WRAPPED_METHOD


def is_builtin_cls(annotation) -> [NotSetType, bool]:
    return NotSet if annotation is NotSet else annotation.__module__ == 'builtins'


def get_deps_from_argspec(spec: FullArgSpec, is_private=False) -> Sequence[Arg]:
    result = []

    defaults_idx_base = (0 if spec.defaults is None else len(spec.defaults)) - len(spec.args)
    n = 0
    for i, name in enumerate(spec.args):
        if name == 'self':
            continue
        default_idx = defaults_idx_base + i
        default = spec.defaults[default_idx] if default_idx >= 0 else NotSet
        annotation = spec.annotations.get(name, NotSet)
        result.append(Arg(name, annotation, default, is_private))
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


def get_method_args(cls, method_name, is_private=False) -> Sequence[Arg]:
    method = getattr(cls, method_name)

    assert method, 'Missing method {1} on class {0}'.format(cls.__name__, method_name)

    assert isinstance(method, Callable), \
        '"{0}.{1}" must be Callable'.format(cls.__name__, method_name)

    spec = getfullargspec(method)
    return get_deps_from_argspec(spec, is_private)


def has_private_injection(cls) -> bool:
    init_method = getattr(cls, '__init__')

    if not init_method:
        return False

    spec = getfullargspec(init_method)

    try:
        if spec.kwonlyargs and spec.kwonlyargs.index(DEPENDENCIES_ARG) >= 0:
            return True
    except ValueError:
        pass

    return False


def get_private_deps(cls) -> Sequence[Arg]:
    args = []

    # Base deps
    for base_cls in cls.__bases__:
        if base_cls.__module__ != 'builtins':
            args += get_private_deps(base_cls)

    # Current deps
    method = getattr(cls, DEPS_METHOD, None)
    if method:
        args += get_method_args(cls, DEPS_METHOD, True)

    return args


def get_public_deps(cls) -> Sequence[Arg]:
    init_method = getattr(cls, '__init__')
    if not init_method:
        return ()

    if has_private_injection(cls):
        real_init = init_method(QUERY_WRAPPED_METHOD)
        spec = getfullargspec(real_init)
        return get_deps_from_argspec(spec)

    else:
        return get_method_args(cls, '__init__')


def get_class_dependencies(cls) -> Sequence[Arg]:
    args = get_private_deps(cls)
    args += get_public_deps(cls)
    return args


def instantiate_class(cls, instance_args: Optional[InstanceArgs] = None, **deps):

    priv_args = get_private_deps(cls)

    # Collect priv args
    priv_deps = {}
    for priv_arg in priv_args:
        key = priv_arg.name
        if key in deps:
            priv_deps[key] = deps[key]

    # Collect public args
    pub_deps = {}
    for key, value in deps.items():
        if key not in priv_deps:
            pub_deps[key] = value

    # Instance args and kwargs
    if instance_args:
        args = instance_args.args
        kwargs = instance_args.kwargs
    else:
        args = ()
        kwargs = {}

    # Instance
    if priv_deps:
        return cls(*args, **{DEPENDENCIES_ARG: priv_deps, **pub_deps, **kwargs})
    else:
        return cls(*args, **{**pub_deps, **kwargs})
