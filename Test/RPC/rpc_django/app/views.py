import json, os
import re
import uuid
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from app.models import *
from django import forms
from concurrent.futures import ThreadPoolExecutor
from app.tool.rpc_spider import RpcSpider
from app.tool.data_process import *
from app.tool.redis_conn import *


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
            return redirect('/task/list')
        else:
            return render(request, 'index.html', {'form': form})


def task_list(request):
    queryset = Task.objects.all()
    return render(request, 'task_list.html', {"queryset": queryset})


@csrf_exempt
def task_run(request):
    if request.method == 'POST':
        executor = ThreadPoolExecutor(20)
        task_id = request.POST.get('id')
        json_data = {
            "status": True,
            "task_id": task_id,
            'data': 'task running...'
        }
        task_obj = Task.objects.filter(id=task_id).first()
        datenow = get_datetime_now(rule="%Y-%m-%d %H:%M:%S")
        executor.submit(rpc_task, task_obj.task_name, task_obj.task_uuid)
        Task.objects.filter(id=task_id).update(status=1, start_time=datenow, end_time=None)
        return JsonResponse(json_data)


@csrf_exempt
def task_stop(request):
    if request.method == 'POST':
        print(111111)
        redisronn = redis_conn()
        task_id = request.POST.get('id')
        json_data = {
            "status": True,
            "task_id": task_id,
            'data': 'task running...'
        }
        task_obj = Task.objects.filter(id=task_id).first()
        path = f'rpcfile:{task_obj.task_uuid}:config:'
        redis_obj = redisronn.get_data(path)
        redis_obj = json.loads(redis_obj)
        pid = redis_obj.get('pid')
        if pid:
            datenow = get_datetime_now(rule="%Y-%m-%d %H:%M:%S")
            Task.objects.filter(id=task_id).update(status=2, end_time=datenow)
            try:
                kill_pid(pid)
            except:
                pass
            return JsonResponse(json_data)
        else:
            raise ValueError('停止失败')

@csrf_exempt
def task_del(request):
    if request.method == 'POST':
        task_id = request.POST.get('id')
        json_data = {
            "status": True,
            "task_id": task_id,
            'data': 'task del...'
        }
        task_obj = Task.objects.filter(id=task_id).delete()
        # executor.submit(rpc_task, 'hello', 123)
        return JsonResponse(json_data)


# 耗时任务
def rpc_task(url, task_id):
    RpcSpider(url=url, task_id=task_id)
    print("Task is done!")


def kill_pid(pid):
    pid = pid
    cmd = 'taskkill /pid ' + str(pid) + ' /f'
    os.system(cmd)
