from django.views.decorators.http import require_POST
from django.http import HttpResponse
from .models import User


@require_POST
def bot_endpoint(request):
    user, created = User.objects.get_or_create(user_id=user_id)
    if not user.is_active:
        pass  # TODO: implement

    module = user.get_module()
    module.dispatch(...)

    return HttpResponse(status=200)
