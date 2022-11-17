from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import datetime, os, time
from django.http import JsonResponse, HttpResponse

# 实例化调度器
scheduler = BackgroundScheduler()
# 调度器使用默认的DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), 'default')


# 每天8点半执行这个任务


def test_add_task(request):
    timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(timenow)
    job = scheduler.add_job(test, 'date', run_date=timenow, args=['test'])
    jobid = job.id
    print(jobid)
    return JsonResponse({'status': 'OK', 'ID': jobid})


def jobs(request):
    get_jobs = scheduler.get_jobs()
    print(get_jobs)
    return HttpResponse('ok')


def resume_job(request, ids):
    jobs = scheduler.resume_job(job_id=str(ids))
    print(jobs)
    return HttpResponse('ok')


def pause_job(request, ids):
    jobs = scheduler.pause_job(job_id=str(ids))
    print(jobs, ids)
    return HttpResponse(jobs)


def test(s):
    # 具体要执行的代码
    print(11111)
    for i in range(10):
        print(i, s, os.getpid())
        time.sleep(i)


# 注册定时任务并开始
register_events(scheduler)
scheduler.start()
