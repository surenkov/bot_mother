from ..base import BaseModule
from importlib import import_module


def module_qualname(module):
    """
    Module qualname (<packages>:<classes>) from module
    :param module: BaseModule or it's instance
    :return: str
    """
    if isinstance(module, BaseModule):
        module = type(module)

    if issubclass(module, BaseModule):
        return '%s:%s' % (module.__module__, module.__qualname__)


def module_type(value):
    """
    Module type from it's instance, type or qualname
    :param value: BaseModule, it's instance or qualname string
    :return: BaseModule subclass
    """
    if isinstance(value, BaseModule):
        return type(value)

    if issubclass(value, BaseModule):
        return value

    if type(value) is str:
        package, module_type_name = value.rsplit(':', 1)
        return getattr(import_module(package), module_type_name)
