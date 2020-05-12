from functools import wraps

from .core import QUERY_WRAPPED_METHOD
from .locators import Locator
from .injector import Injector


def deps(init_method):
    """
     - The `@deps` decorator on `__init__` enables _private injection_.
     - The special method `__deps__` define which dependencies are required.
     - All the dependencies are located and injected before the object is initialized.
     - Finally, the real `__init__` method is called.

    Notice that `__deps__` is a mock method, it is not ever called.
    Its sole purpose is to define the dependencies through its argument signature.
    """
    assert init_method.__name__ == '__init__', \
        '"{}" decorator must precede __init__ method.'.format(deps.__name__)

    @wraps(init_method)
    def init_wrapper(self, *args, _dependencies=None, **kwargs):
        # Query wrapped init
        if self == QUERY_WRAPPED_METHOD:
            return init_method

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
    """
    @inject inspects the arguments of the wrapped function signature and inject the required dependencies.
    You get all the needed dependencies through the function arguments.

    It takes one or more Locator objects as arguments such as Dependencies or Autowiring. They will used to create an
    Injector object which will be used to perform the injection process.

    Alternative, you can pass directly an Injector object through the named argument "injector". In this case,
    do not pass Locator objects.

    """
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
