import uuid
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from app.models import *


# Create your views here.
def index(request):
    return render(request, 'index.html')


def task_list(request):
    queryset = Task.objects.all()
    print(queryset)
    return render(request, 'task_list.html')


@csrf_exempt
def task_add(request):
    if request.method == 'POST':
        task_data = request.POST.get('data', '')
        task_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, task_data)
        json_data = {
            "status": True,
            "task_uuid": task_uuid,
            'data': task_data
        }

        Task.objects.create(task_name=task_uuid, )
        return JsonResponse(json_data)
    else:
        return JsonResponse({'status': False, 'data': 'request methon errors!'})
