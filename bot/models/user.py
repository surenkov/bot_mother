from django.db import models
from . import fields

from bot.modules.helpers import module_qualname, module_type


def default_context():
    return dict(history=list())


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    context = fields.SerializedField(default=default_context)
    module_type = fields.ModuleTypeField(null=True)

    def get_module(self):
        return self.module_type(self.context, self)

    def push_module(self, new_module):
        self.context['history'].append(module_qualname(self.module_type))
        self.module_type = module_type(new_module)

    def pop_module(self):
        module_name = self.context['history'].pop()
        self.module_type = module_type(module_name)
        return self.get_module()

