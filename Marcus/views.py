from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from .models import RemoteCamera, Frame
from django import forms
from django.views.decorators.csrf import csrf_exempt

BASE_IMAGE_DIR = "./"

import json
import uuid

class UploadFileForm(forms.Form):
    camera_uuid = forms.CharField(36)
    frame = forms.FileField()

def index(request):
    if request.method == "POST":
        if "new_camera_uuid" in method.POST:
            new_camera = RemoteCamera.objects.create(name=new_camera_name,
                                                uuid=new_camera_uuid)
            new_camera.save()                
    camera_list = RemoteCamera.objects.all()
    template = loader.get_template('Marcus/index.html')
    context = {
    "camera_list": camera_list
    }
    return HttpResponse(template.render(context, request))

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
                new_frame = Frame.objects.create(owner=camera,url=new_frame_url)
                return HttpResponse("{\"success\":true,\"url\":" + new_frame_url + "}")
            except ObjectDoesNotExist:
                return HttpResponse("{\"success\":false,\"error\":\"Unregistered camera UUID\"}")
    else:
        form = UploadFileForm()
    return HttpResponse(render(request,"Marcus/upload_image.html",{"form":form}))

@csrf_exempt
def json_api(request):
    json_data_in = json.loads(request.body);
    if 'action' in json_data_in:
        if json_data_in['action'] == "newCamera":
            new_camera = RemoteCamera.objects.create(name=json_data_in['newCameraIdentifier'],
                                                    uuid=json_data_in['newCameraUuid'])
            new_camera.save()
            return HttpResponse(str(json_data_in))
    return HttpResponse("{\"success\":false}")
