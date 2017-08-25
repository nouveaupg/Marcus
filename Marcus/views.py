from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from .models import RemoteCamera, Frame
from django import forms
from django.views.decorators.csrf import csrf_exempt

BASE_IMAGE_DIR = "/usr/share/nginx/html/uploaded_files/"

import json
import uuid
import re

class UploadFileForm(forms.Form):
    camera_uuid = forms.CharField(36)
    frame = forms.FileField()

@csrf_exempt
def index(request):
    if request.method == "POST":
        if "new_camera_uuid" in request.POST:
            new_camera_uuid = request.POST['new_camera_uuid']
            new_camera_name = request.POST['new_camera_name']
            new_camera = RemoteCamera.objects.create(name=new_camera_name,
                                                uuid=new_camera_uuid)
            new_camera.save()
        if "remove_camera_id" in request.POST:
            value = int(request.POST['remove_camera_id'])
            try:
                camera_to_remove = RemoteCamera.objects.get(id=value)
                camera_to_remove.delete()
            except:
                raise
    camera_list = RemoteCamera.objects.all()
    template = loader.get_template('Marcus/index.html')
    context = {
    "camera_list": camera_list
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
def latest_still(request):
    path_string = str(request.path)
    camera_number = int(path_string.split("/")[2])
    try:
        camera = RemoteCamera.objects.get(id=camera_number)
        camera_stills = Frame.objects.filter(owner=camera)
        latest_still = camera_stills.latest("timestamp")
        f = file(BASE_IMAGE_DIR + str(latest_still.url),"r")
        jpeg_data = f.read()
        return HttpResponse(jpeg_data,content_type="image/jpeg")
    except:
        raise
    return HttpResponse("Not found.")

@csrf_exempt
def upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST,request.FILES)
        if "camera_uuid" in request.POST:
            camera_uuid = request.POST['camera_uuid']
            try:
                camera = RemoteCamera.objects.get(uuid=camera_uuid)
                new_frame_url = str(uuid.uuid4()) + ".jpg"
                with open(BASE_IMAGE_DIR + new_frame_url, 'wb+') as destination:
                    for chunk in request.FILES['jpeg_upload'].chunks():
                        destination.write(chunk)
                request_ip_addr = request.META['REMOTE_ADDR']
                new_frame = Frame.objects.create(owner=camera,url=new_frame_url)
                camera.ip_addr = request_ip_addr
                camera.save()
                return HttpResponse("{\"success\":true,\"url\":\"" + new_frame_url + "\"}")
            except ObjectDoesNotExist:
                return HttpResponse("{\"success\":false,\"error\":\"Unregistered camera UUID\"}")
    else:
        form = UploadFileForm()
    return HttpResponse(render(request,"Marcus/upload_image.html",{"form":form}))

@csrf_exempt
def json_api(request):
    json_data_in = json.loads(request.body);
    if 'action' in json_data_in:
        if json_data_in['action'] == "getCameraData":
            output = {}
            camera_list = RemoteCamera.objects.all()
            for each_camera in camera_list:
                all_frames = Frame.objects.filter(owner=each_camera.id)
                frame_list = all_frames.values_list()
                frame_count = len(all_frames)
                if frame_count > 0:
                    earliest_frame = frame_list[0]
                    latest_frame = frame_list[frame_count-1]
                    output[each_camera.uuid] = {
                        "frames":frame_count,
                        "earliest_frame_timestamp":earliest_frame[3].isoformat(),
                        "latest_frame_timestamp":latest_frame[3].isoformat(),
                        "latest_frame_url":latest_frame[2]
                    }
                else:
                    output[each_camera.uuid] = {"frames":0}
            return HttpResponse(json.dumps({
                "success":True,
                "cameras":output
            }))
    return HttpResponse("{\"success\":false}")
