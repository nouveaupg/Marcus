from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import RemoteCamera, Frame
from django import forms
from django.views.decorators.csrf import csrf_exempt

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import random
import json
import uuid

class UploadFileForm(forms.Form):
    camera_uuid = forms.CharField(36)
    frame = forms.FileField()

def index(request):
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
        s3 = boto.connect_s3()
        bucket = s3.get_bucket(uuid.uuid4())
        bucket_key = str(uuid.uuid4()) + ".jpg"
        k = Key(bucket)
        k.key = bucket_key
        try:
            k.set_contents_as_string(request.FILES['jpeg_upload'].read())
        except e:
            return HttpResponse("{\"succuss\":false,\"exception\":\"%s\"}" % str(e))
        k.set_acl('public-read')

        return HttpResponseRedirect("https://s3.amazonaws.com/" + bucket + "/" + bucket_key)
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
    return HttpResponse("{\"succuss\":false}")
