from typing import Sequence, Optional

from .core import Locator, Arg, Dependency


class LocatorChain(Locator):
    def __init__(self, *locator_list: Locator):
        self.locator_list = locator_list

    def initialize(self, injector):
        for finder in self.locator_list:
            finder.initialize(injector)

    def get(self, creation_path: Sequence[Arg]):
        for finder in self.locator_list:
            result = finder.get(creation_path)
            if result is not None:
                return result
        return None


class LocatorCache(Locator):
    def __init__(self, locator: Locator):
        self.real_locator = locator
        self.cache = {}

    def initialize(self, injector):
        self.real_locator.initialize(injector)

    def get(self, creation_path: Sequence[Arg]) -> Optional[Dependency]:

        key = hash(creation_path)

        try:
            return self.cache[key]

        except KeyError as ex:
            result = self.real_locator.get(creation_path)
            self.cache[key] = result
            return result
