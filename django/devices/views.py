from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import HttpResponse
from celery import Celery
from celery.result import AsyncResult
import csv
from io import StringIO
import json
from . import allowed_devices
from pprint import pprint
import os

def connect(request):
    context = {}

    if request.method == "POST":
        clientName = request.POST.get("clientName")
        userName = request.POST.get("userName")
        password = request.POST.get("password")

        commands = {}
        response = dict(request.POST)
        for deviceType in allowed_devices.devices:
            if response.get(deviceType):
                command = response.get(deviceType)
                commands[deviceType] = command
            else:
                continue
        
        if request.FILES and clientName and userName and password and commands:

            if not clientName.isalnum():
                messages.info(request, "Client Name should be only alphanumeric characters")
                return redirect("index")

            if not userName.isalnum():
                messages.info(request, "Username should be only alphanumeric characters")
                return redirect("index")

            pfile = request.FILES.get("uploaded file").read().decode("UTF-8")
            deviceList = csv.DictReader(StringIO(pfile))
            context["devices"] = []

            globalDevices = {}
            pprint(commands)
            for device in deviceList:
                device_type = device["device_type"]
                if commands.get(device_type):
                    device["username"] = userName
                    device["password"] = password
                    try:
                        globalDevices[device_type]["device_list"].append(device)
                        
                    except KeyError:
                        globalDevices[device_type] = {"device_list": [], "commands": []}
                        globalDevices[device_type]["device_list"].append(device)
                        globalDevices[device_type]["commands"].extend(commands[device_type])
                else:
                    messages.info(request, "Please provide at least one command per device type")
                    return redirect("index")

            for devicet in globalDevices.keys():
                print(devicet)
                for device in globalDevices[devicet]["device_list"]:
                    print(device)
                    context["devices"].append(device)

            pprint(globalDevices)
            context["table_head"] = context["devices"][0].keys()

            # Create task and send it to the backend Celery worker using Rabbitmq
            app = Celery('tasks', backend='redis://redis/', broker='pyamqp://cisco:cisco@rabbitmq/app')
            task = app.send_task("task.add", args=[clientName, globalDevices])
            context["metaData"] = {
                "taskId": task.id,
                "clientName": clientName
                }

        else:
            context["values"] = request.POST 
            messages.info(request, "All fields are required")
            return redirect("index")
            
    return render(request, "devices/connect.html", context)

def progress(request):

    task_id = request.GET["task_id"]
    app = Celery('tasks', backend='redis://redis/', broker='pyamqp://cisco:cisco@rabbitmq/app')
    progress = app.AsyncResult(task_id)
    response_data = {
        "state": progress.state
        }
    if progress.state == "IN PROGRESS":
        if progress.info != 0:
            output = progress.result["progress"] 
            job_lenght = progress.result["total"]
            progress_percentage = progress.result["current"] * 100 // job_lenght
            response_data.update({
                "job_lenght": job_lenght,
                "progress_percentage": progress_percentage,
                "progress": output
            })
    
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def download(request):
    if request.method == "GET":
        fileName = request.GET.get("filename")
        zipFile = open('files/'+fileName, 'rb')
        response = HttpResponse(zipFile, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename='+fileName
        return response