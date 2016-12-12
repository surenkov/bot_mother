from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


@csrf_exempt
@require_POST
def bot_endpoint(request, token):
    return HttpResponse(status=200)
