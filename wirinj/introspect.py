import sys
from inspect import getfullargspec, signature, Signature, Parameter, _empty
from typing import Sequence, Callable, Optional, get_type_hints

from .core import Arg, NotSet, DEPS_METHOD, FunctionArgs, NotSetType, DEPENDENCIES_ARG, \
    QUERY_WRAPPED_METHOD, InjectionClauses


def is_builtin_cls(annotation) -> [NotSetType, bool]:
    return NotSet if annotation is NotSet else annotation.__module__ == 'builtins'


def get_deps_from_signature(signature: Signature, exclude_first=False) -> Sequence[Arg]:
    result = []

    first = True
    for name, param in signature.parameters.items():
        if first and exclude_first:
            exclude_first = False
            continue
        if param.kind in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
            continue
        annotation = NotSet if param.annotation is _empty else param.annotation
        default = NotSet if param.default is _empty else param.default
        result.append(Arg(name, annotation, default))
    return result



def get_func_result(func: Callable) -> Sequence[Arg]:
    assert isinstance(func, Callable), \
        '"{}" must be Callable'.format(func.__name__)

    sign = signature(func)
    return NotSet if sign.return_annotation is Parameter.empty else sign.return_annotation


def get_func_args(func: Callable) -> Sequence[Arg]:
    assert isinstance(func, Callable), \
        '"{}" must be Callable'.format(func.__name__)

    return get_deps_from_signature(signature(func))


def get_method_args(cls, method_name) -> Sequence[Arg]:
    method = getattr(cls, method_name)

    assert method, 'Missing method {1} on class {0}'.format(cls.__name__, method_name)

    assert isinstance(method, Callable), \
        '"{0}.{1}" must be Callable'.format(cls.__name__, method_name)

    return get_deps_from_signature(signature(method), True)


def has_init_injection(cls) -> bool:
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


def get_signature_deps(cls) -> Sequence[Arg]:
    args = []

    # Base deps
    for base_cls in cls.__bases__:
        if base_cls.__module__ != 'builtins':
            args += get_signature_deps(base_cls)

    # Current deps
    method = getattr(cls, DEPS_METHOD, None)
    if method:
        args += get_method_args(cls, DEPS_METHOD)

    return args


def get_init_deps(cls) -> Sequence[Arg]:
    init_method = getattr(cls, '__init__')
    if not init_method:
        return ()

    if has_init_injection(cls):
        real_init = init_method(QUERY_WRAPPED_METHOD)
        return get_deps_from_signature(signature(real_init), True)

    else:
        return get_method_args(cls, '__init__')


def get_attribute_deps(cls) -> Sequence[Arg]:

    # Field annotations available from Python 3.6
    if (sys.version_info.major == 3 and sys.version_info.minor < 6):
        return []

    result = []
    for field_name, field_class in get_type_hints(cls).items():
        if getattr(cls, field_name) in InjectionClauses:
            result.append(Arg(field_name, field_class, NotSet))
    return result

def get_class_dependencies(cls) -> Sequence[Arg]:

    # __init__ args must come first to know the position of its arguments
    args = get_init_deps(cls)

    args += get_attribute_deps(cls)
    args += get_signature_deps(cls)
    return args



def subclass_inject(cls, args, kwargs, kwinject):

    #Injector = type(cls.__name__, (cls,), {'__metaclass__': WirinjMeta})
    class Injector(cls):
        def __new__(injector_cls, *args, **kwargs):

            super_new = super(Injector, injector_cls).__new__
            if super_new is object.__new__:
                instance = super_new(cls)
            else:
                instance = super_new(cls, *args, **kwargs)

            #Inject
            for name, value in kwinject.items():
                setattr(instance, name, value)

            # Init must be called ourself since we are creating a cls instance and not a injector_cls instance.
            instance.__init__(*args, **kwargs)

            return instance
    return Injector(*args, **kwargs)


def instantiate_class(cls, instance_args: Optional[FunctionArgs] = None, **deps):

    priv_args = get_attribute_deps(cls)
    priv_args += get_signature_deps(cls)

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
        if has_init_injection(cls):
            return cls(*args, **{DEPENDENCIES_ARG: priv_deps, **pub_deps, **kwargs})
        else:
            return subclass_inject(cls, args, {**pub_deps, **kwargs}, priv_deps)
    else:
        return cls(*args, **{**pub_deps, **kwargs})
