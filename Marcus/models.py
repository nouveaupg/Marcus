from django.db import models

class RemoteCamera(models.Model):
    name = models.CharField(max_length=55)
    ip_addr = models.CharField(max_length=55)
    uuid = models.CharField(max_length=36)
    
    def __unicode__(self):
        return self.name

class Frame(models.Model):
    owner = models.ForeignKey(RemoteCamera,on_delete=models.CASCADE)
    s3_location = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(owner) + ": " + timestamp.isoformat()
