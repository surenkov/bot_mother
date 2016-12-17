import pickle
from django.db import models


class SerializedField(models.BinaryField):

    def to_python(self, value):
        if value is None:
            return None
        return pickle.loads(super(SerializedField, self).to_python(value))

    def get_prep_value(self, value):
        if value is None:
            return None
        return super(SerializedField, self).get_prep_value(pickle.dumps(value))
