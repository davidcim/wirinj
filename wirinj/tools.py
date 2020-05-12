from typing import Type


def get_subclassing_factory(cls, func):
    base_cls = cls

    class FactoryMeta(cls.__class__):
        def __call__(cls, *args, **kwargs):
            return func(base_cls, *args, **kwargs)

    class Factory(cls, metaclass=FactoryMeta):
        pass

    return Factory


def get_func_factory(cls, func):
    base_cls = cls

    def factory(*args, **kwargs):
        return func(base_cls, *args, **kwargs)

    return factory


def is_typing_type(cls):
    return cls.__class__ is Type.__class__ and getattr(cls, '_name', getattr(cls, '__name__', None)) == 'Type'

def is_typing_clause(cls):
    return cls.__module__ == 'typing'


def get_typing_args(cls):
    return cls.__args__[0] if cls.__args__ else None


def get_cls_name(cls):
    if is_typing_type(cls):
        args = get_typing_args(cls)
        if args is None:
            a = 1
        return 'Type[{}]'.format(args.__name__)
    else:
        return cls.__name__
