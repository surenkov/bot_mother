from django.db import models
from . import fields


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    state = fields.SerializedField(null=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True)

    def __str__(self):
        full_name = self.first_name + ' ' + self.last_name
        if self.username is not None:
            full_name += ' (@' + self.username + ')'
        return full_name
