import time
import io
import json
import logging
import threading
import requests
import uuid
import os
from picamera import PiCamera

LOG_FORMAT = '%(asctime)-15s %(levelname)s %(message)s'

class UploadWorkerThread(threading.Thread):
    def __init__(self,upload_bytes,logger):
        threading.Thread.__init__(self)
        self.logger = logger
        # load config dict
        self.config = json.load(file("remote-config.json","r"))
        self.uploadUrl = self.config['remote-host'] + "/upload/"
        # stream to upload
        self.uploadStream = io.BytesIO()
        self.uploadStream.write(upload_bytes)
        self.uploadStream.seek(0)
    def run(self):
        start_time = time.time()
        output_data = {"camera_uuid":self.config['uuid']}
        upload_files = [
        ('jpeg_upload', ('jpeg_upload',self.uploadStream,"image/jpeg"))]

        r = requests.post(self.uploadUrl,files=upload_files,data=output_data)
        elapsed = time.time() - start_time
        self.logger.info("Uploaded image to server in %0.2f seconds. (tid %d)" % (elapsed,self.ident))

class CameraMonitor(threading.Thread):
    def __init__(self,timeout=None):
        threading.Thread.__init__(self)
        self.timeout = timeout
        #logging
        FORMAT = '%(asctime)-15s %(message)s'
        self.logger = logging.getLogger(__name__ + ".CameraMonitor")
        fh = logging.FileHandler("CameraMonitor.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(LOG_FORMAT))
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        self.logger.addHandler(fh)
        self.logger.addHandler(sh)
        self.logger.setLevel(logging.DEBUG)
        # load config dict
        self.config = json.load(file("remote-config.json","r"))
        self.uploadUrl = self.config['remote-host'] + "/upload/"
    def run(self):
        camera = PiCamera(resolution=(640,480),framerate=1,sensor_mode=3)
        self.logger.info("Activating camera module with resolution (%d,%d)" % camera.resolution)
        time.sleep(30)
        self.logger.info("Camera ready - beginning capture...")
        stream = io.BytesIO()
        frames = 0

        while 1:
            try:
                camera.capture(stream,"jpeg")
                self.logger.info("Captured image, uploading...")
                worker = UploadWorkerThread(stream.read())
                stream.seek(0)
                stream.truncate()
                frames += 1
                if frames < 5:
                    break
            except e:
                print str(e)
                break

if __name__ == '__main__':
    try:
        f = file("remote-config.json","r")
        config_data = json.load(f)
        if 'uuid' not in config_data:
            config_data['uuid'] = str(uuid.uuid4())
            f.close()
            f = file("remote-config.json","w+")
            f.seek()
            json.dump(config_data,f)
            f.close()
    except IOError:
        # couldn't open file
        print "Couldn't open remote-config.json make sure it exits..."
    print "Starting camera thread with 30 second timeout..."
    monitor = CameraMonitor(30)
    monitor.start()
