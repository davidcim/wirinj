- __Test Python versions__. Test with Python `3.4`, `3.6`, `3.7` y `3.8` and fix issues.

- __docs__. Add `docs` to public API functions and classes.

- __Wildcard definitions__. If `*args` and `**kwargs` are in the signature of the `__init__` or `__deps__` dependencies, allow searching on the definitions
  using a wildcard as the last "tree creation"'s path element to find all the parameters available for the class.

- Allow `Definitions` dicts to have multiple creation paths pointing to a single dependency through `list`s.

- __*Call* definition__. Add `Call`, a new `DependencyBuilder` definition to call a function using its signature as dependency requirements. 

- __Missing parentheses exception__. Explicit exception when you forget the parentheses after `Singleton`, `Instance`, etc. in the definition `dict`.

- __Log *dependency tree* on exception__. Log detailed injection report on exceptions during the instantiation of a class.

- __Dataclasses__. Create `@dependencies` class decorator to inject on [dataclasses](https://docs.python.org/3/library/dataclasses.html).

- __PyCharm plugin__. Create a `PyCharm` plugin which inspects `__deps__` method signature and make all its arguments available as existing member variables.

- __Unit tests__. Create more `Unitests`.

- __Signature()__. Replace `inspect.getfullargspec()` by `inspect.signature()`.
