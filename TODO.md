- __docs__. Add `docs` to public API functions and classes.

- __Wildcard definitions__. If `*args` and `**kwargs` are in the signature of the `__init__` or `__deps__` dependencies, allow searching on the definitions
  using a wildcard as the last "tree creation"'s path element to find all the parameters available for the class.

- __Multi-target definition__. Allow `Definitions` dicts to have multiple instantiation paths pointing to a single dependency through `list`s.

- __*Call* definition__. Add `Call`, a new `DependencyBuilder` definition to call a function using its signature as dependency requirements. 

- __Lazy injection__. `__getattribute__` can be defined in an object so that dependencies are lazily injected only when the injected attributes are accesed for the first time.

- __Missing parentheses exception__. Explicit exception when you forget the parentheses after `Singleton`, `Instance`, etc. in the definition `dict`.

- __Log *dependency tree* on exception__. Log detailed injection report on exceptions during the instantiation of a class.

- __Unit tests__. Create more `Unitests`.

- __core.Arg -> inspect.Parameter__. Replace `Arg` class with built-in `Parameter` class. 
