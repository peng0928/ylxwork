import re
import uuid
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from app.models import *
from django import forms


# Create your views here.

# url 表单验证器
class UrlFrom(forms.Form):
    """验证Book表单"""
    url = forms.CharField(
        required=True,
        error_messages={
            "required": "URL必填",
        },
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'url_input', 'aria-describedby': 'helpBlock2'})
    )

    def clean_url(self):
        url = self.cleaned_data.get('url')
        url_check = re.findall('http://', url) or re.findall('https://', url)
        if not url_check:
            self.add_error('url', '请输入正确的url!')
        return url


@csrf_exempt
def index(request):
    if request.method == 'GET':
        form = UrlFrom()
        return render(request, 'index.html', {'form': form})

    if request.method == 'POST':
        form = UrlFrom(request.POST)
        if form.is_valid():
            task_data = request.POST.get('url', '')
            task_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, task_data)
            json_data = {
                "status": True,
                "task_uuid": task_uuid,
                'data': task_data
            }
            Task.objects.create(task_name=task_data, task_uuid=task_uuid)
            return JsonResponse(json_data)
        else:
            return render(request, 'index.html', {'form': form})


def task_list(request):
    queryset = Task.objects.all()
    return render(request, 'task_list.html', {"queryset": queryset})

def task_run(request):
    pass