from functools import wraps

from .core import Locator
from .injector import Injector


def func_inject(
        dependencies: Locator = None,
        injector: Injector = None,
):
    if injector:
        assert not dependencies,\
            '"{}" decorator requires one argument only, two provided.'.format(func_inject.__name__)
        inj = injector
    elif dependencies:
        inj = Injector(dependencies)
    else:
        raise AssertionError('"{}" decorator requires one single argument, none provided.'.format(func_inject.__name__))

    def get_func_wrapper(func):

        def func_wrapper(*args, **kwargs):
            return inj.call(func, *args, **kwargs)
        return func_wrapper

    return get_func_wrapper


def inject(init_method):

    assert init_method.__name__ == '__init__', \
        '"{}" decorator must precede __init__ method.'.format(inject.__name__)

    @wraps(init_method)
    def init_wrapper(self, *args, dependencies=None, **kwargs):
        # Inject
        if dependencies:
            for name, value in dependencies.items():
                setattr(self, name, value)

        # run __init__
        init_method(self, *args, **kwargs)

    return init_wrapper
