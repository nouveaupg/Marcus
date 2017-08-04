from django.http import HttpResponse
from django.template import loader
from .models import RemoteCamera, Frame
from .forms import UploadImageForm
from django.views.decorators.csrf import csrf_exempt

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import random
import json
import uuid

AWS_ACCESS_KEY="AKIAIPRAN234JWT4WHSQ"
AWS_ACCESS_SECRET_KEY="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"

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
        form = UploadImageForm(request.POST,request.FILES)
        s3 = S3Connection(AWS_ACCESS_KEY,AWS_ACCESS_SECRET_KEY)
        bucket = s3.get_bucket("littlemarco")
        bucket_key = str(uuid.uuid4()) + ".jpg"
        k = Key(bucket)
        k.key = bucket_key
        k.set_contents_as_string(request.FILES['jpeg'])
        k.set_acl('public-read')

        return HttpResponse("https://s3.amazonaws.com/littlemarco/" + bucket_key
        #
        #s3 = S3Connection(AWS_ACCESS_KEY,AWS_ACCESS_SECRET_KEY);
        #if s3:
        #    s3.get_bucket("uuid")


    return HttpResponse("{\"success\":false,\"error\":\"Invalid HTTP method only POST allowed.\"}")

@csrf_exempt
def json_api(request):
    json_data_in = json.loads(request.body);
    if 'action' in json_data_in:
        if json_data_in['action'] == "newCamera":
            new_camera = RemoteCamera.objects.create(name=json_data_in['newCameraIdentifier'],
                                                    ip_addr=json_data_in['newCameraIP'])
            new_camera.save()
            return HttpResponse(str(json_data_in))
    return HttpResponse("{\"succuss\":false}")
