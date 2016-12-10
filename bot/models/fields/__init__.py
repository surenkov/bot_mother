import pickle

from django.db import models
from django.core.exceptions import ValidationError

from bot.modules.helpers import module_qualname, module_type


class SerializedField(models.BinaryField):

    def to_python(self, value):
        return pickle.loads(super().to_python(value))

    def get_prep_value(self, value):
        bytes_value = pickle.dumps(value)
        return super().get_prep_value(bytes_value)


class ModuleTypeField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        module_cls = module_type(super().to_python(value))
        if module_cls is None and value is not None:
            raise ValidationError('Cannot convert value to Module class')
        return module_cls

    def get_prep_value(self, value):
        return super().get_prep_value(module_qualname(value))
