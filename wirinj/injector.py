from logging import ERROR, INFO, DEBUG
from typing import Union, Sequence, Callable, Optional, Dict, Tuple

from .core import logger, Arg, Dependency, NotSet, Locator, SEPARATOR_OPEN, SEPARATOR_CLOSE, FunctionArgs, \
    filter_direct_args, InjectionClauses
from .errors import MissingDependenciesError
from .introspect import get_func_args
from .locators import LocatorChain, LocatorCache


class NotFoundType(type):
    def __str__(self):
        return 'NotFound'


class NotFound(metaclass=NotFoundType):
    pass


class FailedType(type):
    def __str__(self):
        return 'Failed'


class Failed(metaclass=FailedType):
    pass


class CreationNode:
    def __init__(self,
                 arg: Arg,
                 dep: Union[Dependency, NotFoundType, None],
                 childs: Sequence['CreationNode'] = (),
                 ):
        self.arg = arg
        self.dep = dep
        self.childs = childs
        self.instance = None

    def get_params(self):
        result = {}
        for child in self.childs:
            result[child.arg.name] = child.instance
        return result

    def __str__(self) -> str:
        return "{}{}".format(
            str(self.arg),
            ' *** {} ***'.format(str(self.dep)) if self.dep is NotFound else '',
        )


class CreationNodeReference:
    def __init__(self, creation_path: Sequence[CreationNode], node: CreationNode):
        self.creation_path = creation_path
        self.node = node

    def __str__(self) -> str:
        path = ''
        for entry in self.creation_path:
            path += '    '

        return "{}{}".format(
            path,
            str(self.node),
        )


def get_tree_index(root: CreationNode, creation_path=()) -> Sequence[CreationNodeReference]:
    result = []
    for child in root.childs:
        result += get_tree_index(child, (list(creation_path) + [root.arg]))

    result += [CreationNodeReference(creation_path, root)]

    return result


def get_creation_args(node_childs: Sequence[CreationNode]) -> Dict:
    result = {}
    for child in node_childs:
        result[child.arg.name] = child.instance
    return result


def log_creation_tree(tree: CreationNode, log_level=INFO, msg=None):
    if not logger.isEnabledFor(log_level):
        return

    dep_flat = get_tree_index(tree)

    logger.log(log_level, SEPARATOR_OPEN)
    if msg:
        logger.log(log_level, msg)
    for node_ref in dep_flat:
        logger.log(log_level, str(node_ref))
    logger.log(log_level, SEPARATOR_CLOSE)


def _after_tree_creation(success: bool, tree: CreationNode):
    if success:
        log_creation_tree(tree, DEBUG)
    else:
        log_creation_tree(tree, ERROR, 'Missing dependencies:')
        raise MissingDependenciesError('Missing dependencies.')


def creation_path_as_text(parent_path: Sequence[Arg], creation_node: CreationNode, suffix=''):
    path = ''
    for entry in parent_path:
        path += str(entry) + ' -> '

    path += str(creation_node.arg)

    if suffix:
        path += ' [{}]'.format(suffix)

    return path


def has_a_valid_default(arg: Arg):
    if arg.default is NotSet:
        return False

    if arg.cls != NotSet and arg.default in InjectionClauses:
        return False

    return True


class DefaultDependency(Dependency):

    def __init__(self, default):
        self.default = default

    def get_instance(self, instance_args=None, **deps):
        return self.default


class Injector:
    """
    Dependency injection service.
    """

    def __init__(self, *dependencies: Locator, cached=True):
        """
        @param dependencies: one or more Locator objects such as Dependencies or Autowiring which will be queried
        by the injector object to locate dependencies. If two Locators contain the same dependency, the first takes
        precedence.
        @param cached: if True, cached copies of already located dependecy managers (Dependency) are kept to save time.
        """

        assert dependencies, '{0} requires at least one {1}'.format(Injector.__name__, Locator.__name__)

        if len(dependencies) == 1:
            deps = dependencies[0]
        else:
            deps = LocatorChain(*dependencies)

        self.locator = LocatorCache(deps) if cached else deps

        self.locator.initialize(self)

    def get(self, cls, *args, **kwargs):
        success, root = self._create_node((), Arg(None, cls), FunctionArgs(args, kwargs))
        _after_tree_creation(success, root)
        return root.instance

    def call(self, func: Callable, *args, **kwargs):
        injected_args = self._get_function_args(func, args, kwargs)
        return func(*args, **{**injected_args, **kwargs})

    def get_wrapper(self, func: Callable):
        def func_wrapper(*args, **kwargs):
            injected_args = self._get_function_args(func, args, kwargs)
            return func(*args, **{**injected_args, **kwargs})

        return func_wrapper

    def _get_function_args(self, func: Callable, args, kwargs):
        fn_args = get_func_args(func)
        injectable_args = filter_direct_args(fn_args, args, kwargs)
        return self._create_virtual_node(injectable_args, Arg(func.__name__, type(func)))

    def _create_childs(self, arg_list: Optional[Sequence[Arg]], creation_path: Sequence[Arg]) -> Tuple[
        bool, Sequence[CreationNode]]:
        """
        @return: Returns two values. The first value is True if the instantiation of all childs succeded. The second
        is the CreationNode list.
        """
        if not arg_list:
            return True, ()

        childs = []
        success = True
        for arg in arg_list:
            child_success, child = self._create_node(creation_path, arg)
            if not child_success:
                success = False
            childs.append(child)
        return success, childs

    def _create_node(self, parent_path: Sequence[Arg], arg: Arg, instance_args: Optional[FunctionArgs] = None) -> Tuple[
        bool, CreationNode]:
        """
        @return: Returns two values. The first value is True if the instantiation succeded. The second is the new
        node. When the Locator cannot find a dependency, the field 'dep' will be set as NotFound.
        """
        current_path = tuple(parent_path) + (arg,)

        # Find in the locator
        dep = self.locator.get(current_path)
        if not dep:
            if has_a_valid_default(arg):
                dep = DefaultDependency(arg.default)
            else:
                return False, CreationNode(current_path[-1], NotFound)

        # Get dependency args
        dep_args = dep.get_dependencies()

        # With args
        if dep_args:
            # Update path with actual class
            cls = dep.get_class()
            if cls is not NotSet and cls != arg.cls:
                current_path = list(parent_path) + [Arg(arg.name, cls, arg.default)]

            # Remove instance args
            if instance_args:
                dep_args = filter_direct_args(dep_args, instance_args.args, instance_args.kwargs)

            # Create childs
            childs_success, childs = self._create_childs(dep_args, current_path)

            # Creation params
            params = get_creation_args(childs)

        # With no args
        else:
            childs = ()
            params = {}
            childs_success = True

        # New CreationNode
        creation_node = CreationNode(current_path[-1], dep, childs)

        # Missing childs dependencies. Return Node with no instance.
        if not childs_success:
            return False, creation_node

        # All dependencies fulfilled. Create instance
        try:
            creation_node.instance = dep.get_instance(instance_args, **params)
        except BaseException as ex:
            creation_node.instance = Failed
            logger.fatal(SEPARATOR_OPEN)
            logger.fatal('Instantiation ERROR:')
            logger.fatal(creation_path_as_text(parent_path, creation_node, ex.__class__.__name__))
            logger.fatal(SEPARATOR_CLOSE)
            raise ex

        # Return full node
        return True, creation_node

    def _create_virtual_node(self, args: Sequence[Arg], root_arg: Arg):

        # Create tree of dependencies
        success, childs = self._create_childs(args, [root_arg])
        root = CreationNode(root_arg, None, childs)
        _after_tree_creation(success, root)
        return root.get_params()
