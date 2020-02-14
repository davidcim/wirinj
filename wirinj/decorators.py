from functools import wraps

from .locators import Locator
from .injector import Injector


def deps(init_method):
    assert init_method.__name__ == '__init__', \
        '"{}" decorator must precede __init__ method.'.format(deps.__name__)

    @wraps(init_method)
    def init_wrapper(self, *args, _dependencies=None, **kwargs):
        # Inject
        if _dependencies:
            for name, value in _dependencies.items():
                setattr(self, name, value)

        # run __init__
        init_method(self, *args, **kwargs)

    return init_wrapper


def inject(*dependencies: Locator,
           injector: Injector = None
           ):
    if injector:
        assert not dependencies, \
            '"{}" decorator requires one argument only, two provided.'.format(inject.__name__)
        inj = injector
    elif dependencies:
        inj = Injector(*dependencies)
    else:
        raise AssertionError('"{0}" decorator requires an {1} or some {1}s, nothing provided.'
                             .format(inject.__name__, Injector.__name__, Locator.__name__))

    def get_func_wrapper(func):

        def func_wrapper(*args, **kwargs):
            return inj.call(func, *args, **kwargs)

        return func_wrapper

    return get_func_wrapper
